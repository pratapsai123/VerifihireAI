const express = require("express");
const cors = require("cors");
const Docker = require("dockerode");
const tar = require("tar-stream");
const { v4: uuidv4 } = require("uuid");
const { PassThrough, Readable } = require("stream");

const app = express();
app.use(cors());
app.use(express.json({ limit: "50mb" }));

// Connect to Docker
const docker = new Docker();

function detectJavaMainClass(source) {
  if (!source) return "Main";

  // 1. Look for public class (highest priority as it enforces filename)
  const publicMatch = source.match(/public\s+class\s+([A-Za-z0-9_$]+)/);
  if (publicMatch && publicMatch[1]) {
    return publicMatch[1];
  }

  // 2. Look for explicit class containing main
  // Search backwards from 'public static void main' for the nearest 'class Name'
  const mainIndex = source.indexOf("public static void main");
  if (mainIndex !== -1) {
    const prefix = source.substring(0, mainIndex);
    const classRegex = /class\s+([A-Za-z0-9_$]+)/g;
    let match;
    let lastClassMatch = null;
    while ((match = classRegex.exec(prefix)) !== null) {
      lastClassMatch = match[1];
    }
    if (lastClassMatch) return lastClassMatch;
  }

  // 3. Fallback to first class found
  const classMatch = source.match(/class\s+([A-Za-z0-9_$]+)/);
  if (classMatch && classMatch[1]) {
    return classMatch[1];
  }

  return "Main";
}

function toInt(value, fallback) {
  const n = Number.parseInt(value, 10);
  return Number.isFinite(n) ? n : fallback;
}

function normalizeNewlines(s) {
  return String(s ?? "").replace(/\r\n/g, "\n");
}

function normalizeOutput(s) {
  const text = normalizeNewlines(s);
  // Split by newline, trim end of each line, join, then trim the whole result
  return text.split("\n").map(l => l.trimEnd()).join("\n").trim();
}

function normalizeSqlOutput(s) {
  const text = normalizeNewlines(s).trim();
  if (!text) return "";

  const lines = text.split("\n")
    .map(l => l.trim())
    .filter(l => l); // Remove empty lines

  // Filter out table separator lines. 
  // Matches lines containing only -, +, |, and whitespace
  const separatorRegex = /^[\s\-\+\|]+$/;
  // Filter "(N rows)" or "(N row)" footer from Postgres
  const rowCountRegex = /^\(\d+ rows?\)$/;

  const dataLines = lines.filter(l => {
    if (separatorRegex.test(l)) return false;
    if (rowCountRegex.test(l)) return false;
    return true;
  });

  // Remove the header row so column aliases don't affect the result
  if (dataLines.length > 0) {
    dataLines.shift();
  }

  // Normalize internal whitespace: 
  // 1. Replace | with space (for MySQL/Postgres borders)
  // 2. Replace seq of spaces with single space
  return dataLines.map(l => l.replace(/\|/g, " ").split(/\s+/).join(" ").trim()).join("\n");
}

function demuxDockerMultiplexedBuffer(buf) {
  const buffer = Buffer.isBuffer(buf) ? buf : Buffer.from(buf || []);
  let pos = 0;
  let out = "";
  let err = "";
  while (pos + 8 <= buffer.length) {
    const streamType = buffer[pos];
    const size = buffer.readUInt32BE(pos + 4);
    const start = pos + 8;
    const end = start + size;
    if (end > buffer.length) break;
    const text = buffer.subarray(start, end).toString("utf8");
    if (streamType === 1) out += text;
    else if (streamType === 2) err += text;
    pos = end;
  }
  return { stdout: out, stderr: err };
}

function buildTarFiles(files) {
  return new Promise((resolve, reject) => {
    const pack = tar.pack();
    const chunks = [];
    pack.on("data", (c) => chunks.push(c));
    pack.on("end", () => resolve(Buffer.concat(chunks)));
    pack.on("error", reject);

    // Add a directory entry for /tmp to ensure permissions if needed (optional)
    // pack.entry({ name: "tmp", type: "directory", mode: 0o777 });

    const list = Array.isArray(files) ? files : [];
    const next = (i) => {
      if (i >= list.length) {
        pack.finalize();
        return;
      }
      const f = list[i];
      pack.entry({ name: f.name, mode: 0o644 }, f.content ?? "", (err) => {
        if (err) return reject(err);
        return next(i + 1);
      });
    };
    next(0);
  });
}

function languageSpec(language, sourceCode, dbEngine) {
  const lang = (language || "").toLowerCase();

  switch (lang) {
    case "python":
      return {
        image: "public.ecr.aws/docker/library/python:3.12-alpine",
        workdir: "/tmp",
        files: [{ name: "main.py", contentName: "source_code" }],
        cmd: ["sh", "-lc", "python -u /tmp/main.py"],
      };
    case "javascript":
    case "js":
      return {
        image: "public.ecr.aws/docker/library/node:20-alpine",
        workdir: "/tmp",
        files: [{ name: "main.js", contentName: "source_code" }],
        cmd: ["sh", "-lc", "node /tmp/main.js"],
      };
    case "java":
      const className = detectJavaMainClass(sourceCode);
      return {
        image: "public.ecr.aws/amazoncorretto/amazoncorretto:21",
        workdir: "/tmp",
        files: [{ name: `${className}.java`, contentName: "source_code" }],
        cmd: ["sh", "-c", `javac /tmp/${className}.java && java -Djava.io.tmpdir=/tmp -cp /tmp ${className}`],
      };
    case "c":
      return {
        image: "public.ecr.aws/docker/library/gcc:14",
        workdir: "/tmp",
        files: [{ name: "main.c", contentName: "source_code" }],
        cmd: ["sh", "-c", "gcc -O2 -pipe /tmp/main.c -o /tmp/a.out && /tmp/a.out"],
      };
    case "cpp":
    case "c++":
      return {
        image: "public.ecr.aws/docker/library/gcc:14",
        workdir: "/tmp",
        files: [{ name: "main.cpp", contentName: "source_code" }],
        cmd: ["sh", "-c", "g++ -O2 -pipe -std=c++17 /tmp/main.cpp -o /tmp/a.out && /tmp/a.out"],
      };
    case "csharp":
    case "c#":
      return {
        image: "mcr.microsoft.com/dotnet/sdk:8.0",
        workdir: "/tmp",
        files: [
          { name: "app.csproj", contentName: "csproj" },
          { name: "Program.cs", contentName: "source_code" },
        ],
        cmd: ["sh", "-c", "dotnet run --project /tmp/app.csproj --nologo -v q 2>&1"],
        env: ["DOTNET_CLI_HOME=/tmp/.dotnet", "XDG_DATA_HOME=/tmp/.local/share"],
        extra: {
          csproj: `<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>disable</Nullable>
    <NoWarn>CS8600;CS8601;CS8602;CS8603;CS8604</NoWarn>
  </PropertyGroup>
</Project>
`,
        },
      };
    case "go":
    case "golang":
      return {
        image: "public.ecr.aws/docker/library/golang:1.21-alpine",
        workdir: "/tmp",
        files: [{ name: "main.go", contentName: "source_code" }],
        cmd: ["sh", "-c", "go run /tmp/main.go 2>&1"],
        env: ["GOCACHE=/tmp/.cache", "GOMODCACHE=/tmp/.modcache", "CGO_ENABLED=0", "GOPROXY=off", "GO111MODULE=off"],
      };
    case "rust":
      return {
        image: "public.ecr.aws/docker/library/rust:1.75-bookworm",
        workdir: "/tmp",
        files: [{ name: "main.rs", contentName: "source_code" }],
        cmd: ["sh", "-c", "rustc /tmp/main.rs -o /tmp/main 2>&1 && /tmp/main 2>&1"],
      };
    case "php":
      return {
        image: "public.ecr.aws/docker/library/php:8.2-cli-alpine",
        workdir: "/tmp",
        files: [{ name: "main.php", contentName: "source_code" }],
        cmd: ["sh", "-c", "php -d \"error_reporting=E_ERROR|E_PARSE\" /tmp/main.php 2>&1"],
      };
    case "ruby":
      return {
        image: "public.ecr.aws/docker/library/ruby:3.2-alpine",
        workdir: "/tmp",
        files: [{ name: "main.rb", contentName: "source_code" }],
        cmd: ["sh", "-c", "ruby /tmp/main.rb 2>&1"],
      };
    case "kotlin":
      return {
        image: "local-kotlin",
        workdir: "/tmp",
        files: [{ name: "Main.kt", contentName: "source_code" }],
        cmd: ["sh", "-c", "kotlinc /tmp/Main.kt -include-runtime -d /tmp/main.jar 2>&1 && java -Djava.io.tmpdir=/tmp -jar /tmp/main.jar 2>&1"],
      };
    case "swift":
      return {
        image: "swift:5.10",
        workdir: "/tmp",
        files: [{ name: "main.swift", contentName: "source_code" }],
        cmd: ["sh", "-c", "swiftc /tmp/main.swift -o /tmp/main 2>&1 && /tmp/main 2>&1"],
      };
    case "dart":
      return {
        image: "dart:stable",
        workdir: "/tmp",
        files: [{ name: "main.dart", contentName: "source_code" }],
        cmd: ["sh", "-c", "dart /tmp/main.dart 2>&1"],
        env: ["DART_Pub_CACHE=/tmp/.pub-cache", "PUB_CACHE=/tmp/.pub-cache"],
      };

      function detectScalaMainClass(source) {
        if (!source) return "Main";

        // 1. Look for @main (Scala 3)
        const mainMatch = source.match(/@main\s+def\s+([A-Za-z0-9_$]+)/);
        if (mainMatch && mainMatch[1]) {
          return mainMatch[1];
        }

        // 2. Look for object extending App
        const objectAppMatch = source.match(/object\s+([A-Za-z0-9_$]+)\s+extends\s+App/);
        if (objectAppMatch && objectAppMatch[1]) {
          return objectAppMatch[1];
        }

        // 3. Fallback: Find any object. 
        // If the user writes "object Solution { def main... }", we want "Solution".
        const objectMatch = source.match(/object\s+([A-Za-z0-9_$]+)/);
        if (objectMatch && objectMatch[1]) {
          return objectMatch[1];
        }

        return "Main";
      }

    case "scala":
      const scalaMain = detectScalaMainClass(sourceCode);
      return {
        image: "sbtscala/scala-sbt:eclipse-temurin-17.0.4_1.7.1_3.2.0",
        workdir: "/tmp",
        files: [{ name: "Main.scala", contentName: "source_code" }],
        cmd: ["sh", "-c", `scalac /tmp/Main.scala 2>&1 && scala -J-Djava.io.tmpdir=/tmp -classpath /tmp ${scalaMain} 2>&1`],
      };
    case "typescript":
    case "ts":
      return {
        image: "local-typescript:stable",
        workdir: "/tmp",
        files: [{ name: "main.ts", contentName: "source_code" }],
        cmd: ["sh", "-c", "tsc /tmp/main.ts && node /tmp/main.js"],
      };
    case "sql":
      const engine = (dbEngine || "sqlite").toLowerCase();

      if (engine === "postgres" || engine === "postgresql") {
        return {
          image: "public.ecr.aws/docker/library/postgres:15-alpine",
          workdir: "/tmp",
          files: [
            { name: "schema.sql", contentName: "schema_sql" },
            { name: "query.sql", contentName: "source_code" },
          ],
          env: ["POSTGRES_PASSWORD=password", "PGDATA=/tmp/pgdata"],
          // Run as postgres user. Use unix socket in /tmp for speed/reliability.
          cmd: [
            "sh",
            "-c",
            `
            # Init DB
            initdb -D /tmp/pgdata --nosync >/dev/null 2>&1
            
            # Start DB with socket in /tmp
            pg_ctl -D /tmp/pgdata -o "-F -k /tmp" start >/dev/null 2>&1
            
            # Wait for socket
            for i in $(seq 1 30); do
               if pg_isready -h /tmp -U postgres >/dev/null 2>&1; then break; fi
               sleep 0.2
            done
            
            # Setup DB
            cat > /tmp/data.sql
            psql -h /tmp -U postgres -f /tmp/schema.sql >/dev/null 2>&1
            psql -h /tmp -U postgres -f /tmp/data.sql >/dev/null 2>&1
            
            # Run Query with nice formatting
            psql -h /tmp -U postgres -P pager=off -f /tmp/query.sql
            `
          ],
          user: "postgres",
        };
      } else if (engine === "mysql") {
        return {
          image: "public.ecr.aws/docker/library/mysql:8.0-debian",
          workdir: "/tmp",
          files: [
            { name: "schema.sql", contentName: "schema_sql" },
            { name: "query.sql", contentName: "source_code" },
          ],
          env: ["MYSQL_ROOT_PASSWORD=password", "MYSQL_DATABASE=testdb"],
          // Run as mysql user. Use /tmp for data and socket.
          cmd: [
            "sh",
            "-c",
            `
            mkdir -p /tmp/mysql
            # Initialize
            mysqld --initialize-insecure --user=mysql --datadir=/tmp/mysql >/dev/null 2>&1
            
            # Start
            mysqld --user=mysql --datadir=/tmp/mysql --skip-networking --socket=/tmp/mysql.sock > /dev/null 2>&1 &
            
            # Wait for socket
            for i in $(seq 1 60); do
               if mysqladmin ping --socket=/tmp/mysql.sock --silent; then break; fi
               sleep 0.5
            done
            
            # Setup
            cat > /tmp/data.sql
            mysql -u root --socket=/tmp/mysql.sock -e "CREATE DATABASE IF NOT EXISTS testdb; USE testdb;"
            mysql -u root --socket=/tmp/mysql.sock testdb < /tmp/schema.sql
            mysql -u root --socket=/tmp/mysql.sock testdb < /tmp/data.sql
            
            # Run Query
            mysql -u root --socket=/tmp/mysql.sock -t testdb < /tmp/query.sql
            `
          ],
          user: "mysql",
        };
      }

      return {
        image: "local-sqlite",
        workdir: "/tmp",
        files: [
          { name: "query.sql", contentName: "source_code" },
          { name: "schema.sql", contentName: "schema_sql" },
        ],
        cmd: ["sh", "-c", "cat > /tmp/data.sql && sqlite3 /tmp/db.sqlite < /tmp/schema.sql && sqlite3 /tmp/db.sqlite < /tmp/data.sql && sqlite3 -header -column /tmp/db.sqlite < /tmp/query.sql"],
      };
    default:
      return null;
  }
}
async function ensureImage(image) {
  if (image === "local-sqlite") {
    try {
      await docker.getImage("local-sqlite").inspect();
      return;
    } catch (_) {
      console.log("Building local-sqlite image...");
      const pack = tar.pack();
      pack.entry({ name: "Dockerfile" }, `FROM public.ecr.aws/docker/library/alpine:3.18
RUN apk add --no-cache sqlite
WORKDIR /tmp
`);
      pack.finalize();
      await new Promise((resolve, reject) => {
        docker.buildImage(pack, { t: "local-sqlite" }, (err, stream) => {
          if (err) return reject(err);
          stream.pipe(process.stdout);
          docker.modem.followProgress(stream, (err2) => err2 ? reject(err2) : resolve());
        });
      });
      console.log("Built local-sqlite image.");
      return;
    }
  }

  if (image === "local-kotlin") {
    try {
      await docker.getImage(image).inspect();
      return;
    } catch (_) {
      console.log("Building local-kotlin image...");
      const pack = tar.pack();
      // Use amazoncorretto:21 which is already available/cached and reliable
      pack.entry({ name: "Dockerfile" }, `FROM public.ecr.aws/amazoncorretto/amazoncorretto:21
RUN yum install -y tar gzip unzip findutils shadow-utils \\
    && curl -L https://github.com/JetBrains/kotlin/releases/download/v1.9.23/kotlin-compiler-1.9.23.zip -o kotlin.zip \\
    && unzip kotlin.zip -d /opt \\
    && rm kotlin.zip \\
    && ln -s /opt/kotlinc/bin/kotlinc /usr/local/bin/kotlinc \\
    && ln -s /opt/kotlinc/bin/kotlin /usr/local/bin/kotlin
`);
      pack.finalize();

      await new Promise((resolve, reject) => {
        docker.buildImage(pack, { t: "local-kotlin:latest" }, (err, stream) => {
          if (err) return reject(err);
          stream.pipe(process.stdout);
          docker.modem.followProgress(stream, (err2, output) => {
            if (err2) return reject(err2);
            // Dockerode might not parse error details correctly sometimes?
            if (output && output.some(evt => evt.error || (evt.errorDetail && evt.errorDetail.code))) {
              return reject(new Error("Build failed: " + JSON.stringify(output.find(evt => evt.error))));
            }
            resolve();
          });
        });
      });
      console.log("Built local-kotlin image.");
      return;
    }
  }

  const imageName = "local-typescript:stable";
  if (image === "local-typescript" || image === imageName) {
    try {
      await docker.getImage(imageName).inspect();
      return;
    } catch (_) {
      console.log(`Building ${imageName} image...`);
      const pack = tar.pack();
      // Install in /tmp so it merges with user code. tsc will find node_modules in current dir.
      pack.entry({ name: "Dockerfile" }, `FROM public.ecr.aws/docker/library/node:20-alpine
WORKDIR /tmp
RUN npm init -y && npm install typescript @types/node
ENV PATH /tmp/node_modules/.bin:$PATH
`);
      pack.finalize();

      await new Promise((resolve, reject) => {
        docker.buildImage(pack, { t: imageName }, (err, stream) => {
          if (err) return reject(err);
          stream.pipe(process.stdout);
          docker.modem.followProgress(stream, (err2, output) => {
            if (err2) return reject(err2);
            if (output && output.some(evt => evt.error || (evt.errorDetail && evt.errorDetail.code))) {
              return reject(new Error("Build failed: " + JSON.stringify(output.find(evt => evt.error))));
            }
            resolve();
          });
        });
      });
      console.log(`Built ${imageName} image.`);
      return;
    }
  }

  try {
    await docker.getImage(image).inspect();
    return;
  } catch (_) {
    // missing
  }
  // Use standard docker.pull
  await new Promise((resolve, reject) => {
    docker.pull(image, (err, stream) => {
      if (err) return reject(err);
      docker.modem.followProgress(stream, (err2) => (err2 ? reject(err2) : resolve()));
    });
  });
}

// Low-level function to run a single execution in a container
async function executeOne({ spec, source_code, stdin, time_limit_ms, memory_mb, schema_sql }) {
  const id = uuidv4();
  const tl = Math.max(1000, toInt(time_limit_ms, 3000));
  const mem = Math.max(128, toInt(memory_mb, 512));

  let container = null;
  let timedOut = false;
  let timeout = null;

  try {
    await ensureImage(spec.image);

    container = await docker.createContainer({
      Image: spec.image,
      WorkingDir: spec.workdir,
      Cmd: spec.cmd,
      Env: spec.env || [],
      User: spec.user,
      OpenStdin: true,
      StdinOnce: true,
      AttachStdin: true,
      AttachStdout: true,
      AttachStderr: true,
      Tty: false,
      NetworkDisabled: true,
      HostConfig: {
        AutoRemove: false,
        Memory: mem * 1024 * 1024,
        PidsLimit: 256,
        Privileged: false,
        ReadonlyRootfs: false,
        CapDrop: ["ALL"],
        SecurityOpt: ["no-new-privileges"],
      },
    });

    const code = normalizeNewlines(source_code);
    const filesToWrite = spec.files.map((f) => {
      if (f.contentName === "source_code") return { name: f.name, content: code };
      if (f.contentName === "schema_sql") return { name: f.name, content: normalizeNewlines(schema_sql || "") };
      if (f.contentName === "csproj") {
        const defaultCsproj = `<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable></PropertyGroup></Project>`;
        return { name: f.name, content: spec.extra?.csproj || defaultCsproj };
      }
      return { name: f.name, content: "" };
    });

    const tarBuffer = await buildTarFiles(filesToWrite);
    await container.putArchive(Readable.from([tarBuffer]), { path: spec.workdir });

    // Stream setup
    const attach = await container.attach({ stream: true, stdin: true, stdout: true, stderr: true });

    let stdout = "";
    let stderr = "";
    let tStart = Date.now();

    await container.start();

    // Write input
    const input = normalizeNewlines(stdin);
    if (input) attach.write(input);
    attach.end();

    // Timeout kill
    timeout = setTimeout(async () => {
      timedOut = true;
      try { await container.kill(); } catch (_) { }
    }, tl);

    // Wait result
    let exitCode = null;
    try {
      const result = await container.wait();
      exitCode = result?.StatusCode ?? null;
      clearTimeout(timeout);

      const logsResult = await new Promise((resolve, reject) => {
        container.logs({ stdout: true, stderr: true, follow: false }, (err, r) => err ? reject(err) : resolve(r));
      });

      if (Buffer.isBuffer(logsResult)) {
        const parsed = demuxDockerMultiplexedBuffer(logsResult);
        stdout += parsed.stdout;
        stderr += parsed.stderr;
      } else {
        stdout += " (Logs unavailable in buffer mode) ";
      }
    } catch (e) {
      if (!timedOut) throw e;
    }

    return {
      ok: true,
      id,
      time_limit_ms: tl,
      memory_mb: mem,
      timed_out: timedOut,
      exit_code: exitCode,
      stdout,
      stderr,
      execution_time_ms: (exitCode !== null && typeof tStart === 'number') ? (Date.now() - tStart) : 0,
    };

  } catch (e) {
    return { ok: false, error: e.message };
  } finally {
    if (timeout) clearTimeout(timeout);
    if (container) {
      try { await container.remove({ force: true }); } catch (_) { }
    }
  }
}

app.get("/health", (req, res) => res.json({ ok: true }));

app.post("/execute", async (req, res) => {
  try {
    const { language, source_code, stdin, time_limit_ms, memory_mb, testcases, schema_sql, database_engine } = req.body || {};

    if (!language || !source_code) {
      return res.status(400).json({ ok: false, error: "language and source_code required" });
    }

    const lowerLang = language.toLowerCase();
    const spec = languageSpec(lowerLang, source_code, database_engine);
    if (!spec) {
      return res.status(400).json({ ok: false, error: `Unsupported language: ${language}` });
    }

    // MODE 1: Batch Testcases
    if (Array.isArray(testcases) && testcases.length > 0) {
      const results = [];
      let passedCount = 0;

      for (const tc of testcases) {
        const t0 = Date.now();
        const res = await executeOne({
          spec,
          source_code,
          stdin: tc.stdin || "",
          time_limit_ms,
          memory_mb,
          schema_sql
        });
        const t1 = Date.now();

        if (!res.ok) {
          results.push({
            testcase_id: tc.id,
            status: "ERROR",
            message: res.error,
            execution_time_ms: 0
          });
          continue;
        }

        let actual, expected;
        if (lowerLang === 'sql') {
          actual = normalizeSqlOutput(res.stdout);
          expected = normalizeSqlOutput(tc.expected_stdout);
        } else {
          actual = normalizeOutput(res.stdout);
          expected = normalizeOutput(tc.expected_stdout);
        }

        let status = "FAIL";
        if (res.timed_out) status = "TIMEOUT";
        else if (res.exit_code !== 0) status = "ERROR";
        else if (actual === expected) status = "PASS";

        if (status === "PASS") passedCount++;

        results.push({
          testcase_id: tc.id,
          status,
          stdout: res.stdout,
          stderr: res.stderr,
          exit_code: res.exit_code,
          timed_out: res.timed_out,
          execution_time_ms: t1 - t0,
          stdin: tc.stdin,
          expected_stdout: tc.expected_stdout
        });
      }

      return res.json({
        ok: true,
        passed_count: passedCount,
        total_tests: testcases.length,
        results
      });
    }

    // MODE 2: Single Run
    const result = await executeOne({ spec, source_code, stdin: stdin || "", time_limit_ms, memory_mb, schema_sql });
    if (!result.ok) {
      return res.status(500).json(result);
    }
    return res.json(result);

  } catch (e) {
    console.error(e);
    res.status(500).json({ ok: false, error: e.message });
  }
});

const port = toInt(process.env.EXECUTOR_PORT, 4000);
app.listen(port, () => {
  console.log(`Executor running on ${port}`);
});
