import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import MainHeader from '../components/MainHeader';
import Footer from '../components/Footer';
import '../styles/FeatureCodingAssessment.css';

// Reusable SVG Icons to ensure zero external dependencies while looking premium
const Icons = {
  Terminal: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>
  ),
  Code: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
  ),
  Shield: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
  ),
  CheckCircle: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
  ),
  Play: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
  ),
  Eye: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
  ),
  Brain: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"></path><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"></path></svg>
  ),
  Database: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>
  ),
  Folder: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
  ),
  File: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg>
  ),
  Settings: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33h.09a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
  )
};

const SUPPORTED_LANGUAGES = [
  'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'TypeScript',
  'Ruby', 'Swift', 'Kotlin', 'PHP', 'Scala', 'R', 'SQL'
];

const IDEMockup = () => {
  const [codeLines, setCodeLines] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCodeLines(prev => (prev < 9 ? prev + 1 : prev));
    }, 600);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="ide-container">
      <div className="ide-glow"></div>

      <div className="ide-body">
        {/* Mac OS Style Header */}
        <div className="ide-header">
          <div className="ide-mac-btns">
            <div className="ide-mac-btn red"></div>
            <div className="ide-mac-btn yellow"></div>
            <div className="ide-mac-btn green"></div>
          </div>
          <div className="ide-title">
            <Icons.Folder /> assessment-project
          </div>
          <div>
            <div className="ide-run-btn">
              <Icons.Play style={{ width: '12px', height: '12px' }} />
              <span>Run Tests</span>
            </div>
          </div>
        </div>

        <div className="ide-main">
          {/* Activity Bar */}
          <div className="ide-activity-bar">
            <Icons.File className="ide-activity-icon active" />
            <Icons.Terminal className="ide-activity-icon" />
            <Icons.Database className="ide-activity-icon" />
            <div style={{ flex: 1 }}></div>
            <Icons.Settings className="ide-activity-icon" />
          </div>

          {/* Explorer Sidebar */}
          <div className="ide-sidebar">
            <div className="ide-sidebar-title">EXPLORER</div>
            <div className="ide-file"><Icons.Folder style={{ color: '#60a5fa' }} /> src</div>
            <div className="ide-file active" style={{ paddingLeft: '2rem' }}><Icons.Code style={{ color: '#eab308' }} /> solution.py</div>
            <div className="ide-file" style={{ paddingLeft: '2rem' }}><Icons.Code style={{ color: '#60a5fa' }} /> utils.ts</div>
            <div className="ide-file" style={{ paddingLeft: '2rem' }}><Icons.Code style={{ color: '#f87171' }} /> main.rs</div>
            <div className="ide-file" style={{ marginTop: '0.5rem' }}><Icons.Folder style={{ color: '#34d399' }} /> tests</div>
            <div className="ide-file" style={{ paddingLeft: '2rem' }}><Icons.Code style={{ color: '#34d399' }} /> test_solution.py</div>
          </div>

          {/* Editor Space */}
          <div className="ide-editor">
            {/* Editor Tabs */}
            <div className="ide-tabs">
              <div className="ide-tab active">
                <Icons.Code style={{ color: '#eab308' }} /> solution.py
              </div>
              <div className="ide-tab">
                <Icons.Code style={{ color: '#34d399' }} /> test_solution.py
              </div>
            </div>

            {/* Code Area */}
            <div className="ide-code-area">
              <div className="ide-line-numbers">
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(n => <div key={n} style={n === 7 ? { color: '#3b82f6', fontWeight: 'bold' } : {}}>{n}</div>)}
              </div>

              <div className="ide-code-content">
                <div>
                  <span style={{ color: '#c084fc' }}>from</span> typing <span style={{ color: '#c084fc' }}>import</span> List, Dict
                </div>

                {codeLines >= 1 && (
                  <div className="animate-fade-in-up" style={{ marginTop: '0.5rem' }}>
                    <span style={{ color: '#c084fc' }}>def</span> <span style={{ color: '#60a5fa', fontWeight: 'bold' }}>find_optimal_path</span>(graph: Dict, start: <span style={{ color: '#86efac' }}>str</span>, end: <span style={{ color: '#86efac' }}>str</span>) -{'>'} List[<span style={{ color: '#86efac' }}>str</span>]:
                  </div>
                )}

                {codeLines >= 2 && (
                  <div className="animate-fade-in-up" style={{ paddingLeft: '1rem', color: '#64748b', fontStyle: 'italic', borderLeft: '2px solid #334155', marginLeft: '0.25rem', marginTop: '0.25rem', marginBottom: '0.25rem' }}>
                    """ Hint: Implementing A* search algorithm for optimal routing """
                  </div>
                )}

                {codeLines >= 3 && (
                  <div className="animate-fade-in-up" style={{ paddingLeft: '1rem' }}>
                    open_set = [(<span style={{ color: '#fb923c' }}>0</span>, start)]
                  </div>
                )}

                {codeLines >= 4 && (
                  <div className="animate-fade-in-up" style={{ paddingLeft: '1rem' }}>
                    came_from = {'{}'}
                  </div>
                )}

                {codeLines >= 5 && (
                  <div className="animate-fade-in-up" style={{ paddingLeft: '1rem' }}>
                    g_score = {'{'}start: <span style={{ color: '#fb923c' }}>0</span>{'}'}
                  </div>
                )}

                {codeLines >= 6 && (
                  <div className="animate-fade-in-up" style={{ marginTop: '0.5rem', backgroundColor: 'rgba(30, 58, 138, 0.2)', padding: '0.125rem 1rem', borderLeft: '2px solid #3b82f6', position: 'relative' }}>
                    <span style={{ color: '#c084fc' }}>while</span> open_set:
                    <div style={{ position: 'absolute', right: '1rem', top: '0.125rem', fontSize: '10px', color: '#93c5fd', backgroundColor: 'rgba(30, 58, 138, 0.6)', padding: '0.125rem 0.5rem', borderRadius: '9999px', display: 'flex', alignItems: 'center', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
                      <Icons.Shield style={{ width: '12px', height: '12px', marginRight: '4px' }} /> Hint: Suggests PriorityQueue
                    </div>
                  </div>
                )}

                {codeLines >= 7 && (
                  <div className="animate-fade-in-up" style={{ paddingLeft: '2rem' }}>
                    current = <span style={{ color: '#bfdbfe' }}>heapq</span>.heappop(open_set)[<span style={{ color: '#fb923c' }}>1</span>]
                  </div>
                )}

                {codeLines >= 8 && (
                  <div className="animate-fade-in-up" style={{ paddingLeft: '2rem', marginTop: '0.25rem' }}>
                    <span style={{ color: '#c084fc' }}>if</span> current == end:
                  </div>
                )}

                {codeLines >= 9 && (
                  <div className="animate-fade-in-up" style={{ paddingLeft: '3rem' }}>
                    <span style={{ color: '#c084fc' }}>return</span> <span style={{ color: '#bfdbfe' }}>reconstruct_path</span>(came_from, current)
                    <span style={{ display: 'inline-block', width: '8px', height: '16px', backgroundColor: '#60a5fa', marginLeft: '4px', transform: 'translateY(4px)', animation: 'pulse 1s infinite' }}></span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Status Bar */}
        <div className="ide-status-bar">
          <div style={{ display: 'flex', gap: '1rem' }}>
            <span className="ide-status-item"><Icons.Code style={{ width: '12px', height: '12px', marginRight: '4px' }} /> Python 3.11</span>
            <span className="ide-status-item">UTF-8</span>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <span className="ide-status-item">Ln 11, Col 42</span>
            <span className="ide-status-item"><Icons.CheckCircle style={{ width: '12px', height: '12px', marginRight: '4px' }} /> Prettier</span>
          </div>
        </div>

        {/* Terminal/Test Results Footer */}
        <div className="ide-terminal">
          <div className="ide-term-tabs">
            <span className="ide-term-tab">TERMINAL</span>
            <span className="ide-term-tab active">TEST OUTPUT</span>
          </div>
          <div className="ide-term-title">
            <Icons.Terminal style={{ width: '12px', height: '12px', marginRight: '8px', color: '#60a5fa' }} />
            EXECUTION PIPELINE
          </div>
          <div style={{ paddingLeft: '0.5rem' }}>
            <div className="ide-term-pass">
              <Icons.CheckCircle style={{ width: '12px', height: '12px', marginRight: '8px' }} />
              <span>[PASS] Test Case 1: Basic Graph Routing (12ms)</span>
            </div>
            <div className="ide-term-pass">
              <Icons.CheckCircle style={{ width: '12px', height: '12px', marginRight: '8px' }} />
              <span>[PASS] Test Case 2: Complex Cycles Detection (45ms)</span>
            </div>
            <div className="ide-term-pass">
              <Icons.CheckCircle style={{ width: '12px', height: '12px', marginRight: '8px' }} />
              <span>[PASS] Test Case 3: Performance/Memory Limit (O(V+E)) (180ms)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', color: '#60a5fa', fontWeight: 'bold', marginTop: '0.75rem', backgroundColor: 'rgba(30, 58, 138, 0.2)', padding: '0.25rem 0.5rem', borderRadius: '0.25rem', width: 'max-content', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
              <span>❯ All 15 edge cases passed successfully. Candidate score: 100%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const CODE_SNIPPETS = {
  Python: [
    "import heapq",
    "",
    "def reconstruct_path(came_from, current):",
    "    path = [current]",
    "    while current in came_from:",
    "        current = came_from[current]",
    "        path.append(current)",
    "    return path[::-1]",
    "",
    "def find_optimal_path(graph, start, end):",
    "    open_set = [(0, start)]",
    "    came_from = {}",
    "    g_score = {start: 0}",
    "",
    "    while open_set:",
    "        current_distance, current = heapq.heappop(open_set)",
    "        if current == end:",
    "            return reconstruct_path(came_from, current)",
    "        # AI Suggestion: Check neighbors",
    "        for neighbor, cost in graph.get(current, {}).items():",
    "            tentative_g_score = g_score[current] + cost",
    "            if tentative_g_score < g_score.get(neighbor, float('inf')):",
    "                came_from[neighbor] = current",
    "                g_score[neighbor] = tentative_g_score",
    "                heapq.heappush(open_set, (tentative_g_score, neighbor))",
    "    return []"
  ],
  JavaScript: [
    "function reconstructPath(cameFrom, current) {",
    "    const path = [current];",
    "    while (cameFrom.has(current)) {",
    "        current = cameFrom.get(current);",
    "        path.push(current);",
    "    }",
    "    return path.reverse();",
    "}",
    "",
    "function findOptimalPath(graph, start, end) {",
    "    const openSet = new PriorityQueue(); // custom PQ class",
    "    openSet.enqueue(start, 0);",
    "    const cameFrom = new Map();",
    "    const gScore = new Map([[start, 0]]);",
    "",
    "    while (!openSet.isEmpty()) {",
    "        const current = openSet.dequeue();",
    "        if (current === end) return reconstructPath(cameFrom, current);",
    "",
    "        for (const [neighbor, cost] of Object.entries(graph[current] || {})) {",
    "            const tentativeG = gScore.get(current) + cost;",
    "            if (tentativeG < (gScore.get(neighbor) || Infinity)) {",
    "                cameFrom.set(neighbor, current);",
    "                gScore.set(neighbor, tentativeG);",
    "                openSet.enqueue(neighbor, tentativeG);",
    "            }",
    "        }",
    "    }",
    "    return [];",
    "}"
  ],
  Java: [
    "import java.util.*;",
    "",
    "class GraphSolver {",
    "    private List<String> reconstructPath(Map<String, String> cameFrom, String current) {",
    "        List<String> path = new ArrayList<>();",
    "        path.add(current);",
    "        while (cameFrom.containsKey(current)) {",
    "            current = cameFrom.get(current);",
    "            path.add(current);",
    "        }",
    "        Collections.reverse(path);",
    "        return path;",
    "    }",
    "",
    "    public List<String> findOptimalPath(Map<String, Map<String, Integer>> graph, String start, String end) {",
    "        PriorityQueue<Node> openSet = new PriorityQueue<>(Comparator.comparingInt(n -> n.cost));",
    "        openSet.add(new Node(start, 0));",
    "        Map<String, String> cameFrom = new HashMap<>();",
    "        Map<String, Integer> gScore = new HashMap<>();",
    "        gScore.put(start, 0);",
    "",
    "        while (!openSet.isEmpty()) {",
    "            Node current = openSet.poll();",
    "            if (current.name.equals(end)) return reconstructPath(cameFrom, current.name);",
    "",
    "            Map<String, Integer> neighbors = graph.getOrDefault(current.name, new HashMap<>());",
    "            for (Map.Entry<String, Integer> entry : neighbors.entrySet()) {",
    "                int tentativeG = gScore.get(current.name) + entry.getValue();",
    "                if (tentativeG < gScore.getOrDefault(entry.getKey(), Integer.MAX_VALUE)) {",
    "                    cameFrom.put(entry.getKey(), current.name);",
    "                    gScore.put(entry.getKey(), tentativeG);",
    "                    openSet.add(new Node(entry.getKey(), tentativeG));",
    "                }",
    "            }",
    "        }",
    "        return new ArrayList<>();",
    "    }",
    "}"
  ]
};

const AdvancedSplitScreenMockup = () => {
  const [codeIndex, setCodeIndex] = useState(0);
  const [proctorState, setProctorState] = useState(0); // 0: clear, 1: tab-switch, 2: copy-paste
  const [pastedCount, setPastedCount] = useState(0);
  const [activeTab, setActiveTab] = useState('coding'); // 'question' or 'coding'
  const [selectedLang, setSelectedLang] = useState('Python');

  // Dynamically pull code for the selected language, or default to Python if not mapped
  const codeSnippet = CODE_SNIPPETS[selectedLang] || CODE_SNIPPETS['Python'];

  useEffect(() => {
    // Reset typing animation on language change
    setCodeIndex(0);
    setProctorState(0);
    setPastedCount(0);

    // Typewriter effect
    const typeInterval = setInterval(() => {
      setCodeIndex(prev => {
        if (prev >= codeSnippet.length) return prev;

        // Trigger proctoring events during typing dynamically based on length
        const mid = Math.floor(codeSnippet.length / 2);

        if (prev === Math.floor(mid * 0.4)) setProctorState(1); // Tab switch
        if (prev === Math.floor(mid * 0.6)) setProctorState(0); // Clear

        // Simulate a massive copy-paste
        if (prev === Math.floor(mid * 0.8)) {
          setProctorState(2);
          // Calculate how many lines to jump (paste)
          const linesToPaste = Math.max(3, Math.floor(codeSnippet.length * 0.3));
          setPastedCount(linesToPaste);
          return prev + linesToPaste; // Jump ahead by multiple lines
        }

        // Clear paste warning later
        if (prev >= Math.floor(mid * 0.8) + Math.max(3, Math.floor(codeSnippet.length * 0.3)) + 4) {
          setProctorState(0);
        }

        return prev + 1;
      });
    }, 1000);

    return () => clearInterval(typeInterval);
  }, [selectedLang, codeSnippet.length]);

  return (
    <div className="fca-split-hero">
      {/* Left Panel: Hero Text */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', minWidth: 0 }}>
        <div style={{ textAlign: 'left' }}>
          <div className="fca-badge" style={{ marginBottom: '1.5rem' }}>
            <span className="fca-badge-dot-container">
              <span className="fca-badge-dot-ping"></span>
              <span className="fca-badge-dot"></span>
            </span>
            <span>Next-Gen Assessment Engine</span>
          </div>

          <h1 className="fca-hero-title" style={{ fontSize: '42px', fontWeight: '800', lineHeight: '1.1', letterSpacing: '-0.04em', textAlign: 'left', margin: '0 0 20px 0' }}>
            Evaluate <br />
            <span className="text-gradient">Engineering Talent</span> <br />
            With Precision.
          </h1>

          <p className="fca-hero-desc" style={{ fontSize: '15px', color: '#475569', lineHeight: '1.75', margin: '0', textAlign: 'left', maxWidth: '460px' }}>
            Move beyond whiteboarding. Assess developers in a secure, browser-based coding environment with automated test cases, AI-driven code analysis, and robust plagiarism detection.
          </p>
        </div>
      </div>

      {/* Right Panel: Interactive IDE & Test Cases with Tabs */}
      <div className="fca-ide-panel" style={{ minWidth: 0, width: '100%' }}>
        <div className="fca-editor-wrapper" style={{ height: '480px' }}>

          {/* Mac OS Header with Tabs */}
          <div className="fca-editor-header" style={{ justifyContent: 'flex-start', gap: '2rem', padding: '0 1rem' }}>
            <div className="ide-mac-btns" style={{ margin: '0.75rem 0' }}>
              <div className="ide-mac-btn red"></div>
              <div className="ide-mac-btn yellow"></div>
              <div className="ide-mac-btn green"></div>
            </div>

            <div style={{ display: 'flex', gap: '1rem', height: '100%' }}>
              <button
                onClick={() => setActiveTab('question')}
                style={{
                  background: 'none', border: 'none', color: activeTab === 'question' ? '#60a5fa' : '#94a3b8',
                  borderBottom: activeTab === 'question' ? '2px solid #60a5fa' : '2px solid transparent',
                  padding: '1rem 0.5rem', cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s', display: 'flex', alignItems: 'center', gap: '0.5rem'
                }}
              >
                <Icons.File style={{ width: '16px', height: '16px' }} /> Problem Statement
              </button>
              <button
                onClick={() => setActiveTab('coding')}
                style={{
                  background: 'none', border: 'none', color: activeTab === 'coding' ? '#60a5fa' : '#94a3b8',
                  borderBottom: activeTab === 'coding' ? '2px solid #60a5fa' : '2px solid transparent',
                  padding: '1rem 0.5rem', cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s', display: 'flex', alignItems: 'center', gap: '0.5rem'
                }}
              >
                <Icons.Code style={{ width: '16px', height: '16px' }} /> Code Editor
              </button>
            </div>
          </div>

          {activeTab === 'question' ? (
            /* Question Tab Content */
            <div style={{ padding: '2rem', overflowY: 'auto', height: '100%', background: 'rgba(15, 23, 42, 0.4)' }}>
              <div className="fca-problem-header" style={{ borderBottom: '1px solid rgba(51,65,85,0.5)', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
                <h2 className="fca-problem-title">Find the Optimal Path</h2>
                <span className="fca-difficulty-badge">Medium</span>
              </div>

              <div className="fca-problem-content">
                <p style={{ marginBottom: '1rem' }}>
                  You are given a weighted, directed graph represented as an adjacency list.
                  Write a function to find the shortest path from the <code>start</code> node to the <code>end</code> node.
                </p>

                <h3 className="fca-problem-section-title" style={{ marginTop: '1.5rem' }}>Input Format:</h3>
                <ul style={{ listStyleType: 'disc', paddingLeft: '1.5rem', marginBottom: '1rem', color: '#94a3b8' }}>
                  <li><code>graph</code>: A dictionary where keys are node strings, and values are dictionaries of neighbor nodes mapped to edge weights.</li>
                  <li><code>start</code>: A string representing the starting node.</li>
                  <li><code>end</code>: A string representing the destination node.</li>
                </ul>

                <h3 className="fca-problem-section-title">Output Format:</h3>
                <p style={{ marginBottom: '1.5rem', color: '#94a3b8' }}>
                  Return a list of strings representing the sequence of nodes in the shortest path. If no path exists, return an empty list <code>[]</code>.
                </p>

                <h3 className="fca-problem-section-title">Example 1:</h3>
                <div className="fca-code-block" style={{ marginBottom: '1.5rem', padding: '1rem', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '0.5rem', border: '1px solid rgba(51,65,85,0.4)', fontFamily: 'monospace', fontSize: '0.85rem' }}>
                  <div style={{ color: '#94a3b8' }}>Input:</div>
                  <div style={{ color: '#e2e8f0', marginBottom: '0.5rem' }}>graph = {'{"A": {"B": 1, "C": 4}, "B": {"C": 2}, "C": {}}'}<br />start = "A", end = "C"</div>
                  <div style={{ color: '#94a3b8' }}>Output:</div>
                  <div style={{ color: '#e2e8f0' }}>["A", "B", "C"]</div>
                  <div style={{ color: '#94a3b8', marginTop: '0.5rem', fontSize: '0.8rem' }}>Explanation: The path A -{'>'} B -{'>'} C has a total weight of 1 + 2 = 3, which is shorter than A -{'>'} C (weight 4).</div>
                </div>

                <h3 className="fca-problem-section-title">Example 2:</h3>
                <div className="fca-code-block" style={{ marginBottom: '1.5rem', padding: '1rem', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '0.5rem', border: '1px solid rgba(51,65,85,0.4)', fontFamily: 'monospace', fontSize: '0.85rem' }}>
                  <div style={{ color: '#94a3b8' }}>Input:</div>
                  <div style={{ color: '#e2e8f0', marginBottom: '0.5rem' }}>graph = {'{"X": {"Y": 5}, "Y": {}}'}<br />start = "X", end = "Z"</div>
                  <div style={{ color: '#94a3b8' }}>Output:</div>
                  <div style={{ color: '#e2e8f0' }}>[]</div>
                  <div style={{ color: '#94a3b8', marginTop: '0.5rem', fontSize: '0.8rem' }}>Explanation: Node Z is unreachable from X.</div>
                </div>

                <h3 className="fca-problem-section-title">Constraints:</h3>
                <ul style={{ listStyleType: 'disc', paddingLeft: '1.5rem', marginTop: '0.5rem', color: '#94a3b8' }}>
                  <li style={{ marginBottom: '0.5rem' }}>1 {'<='} Total Nodes {'<='} 10^4</li>
                  <li style={{ marginBottom: '0.5rem' }}>All edge weights are positive integers {'>'} 0.</li>
                  <li>Must run in <code>O((V+E) log V)</code> time complexity using a priority queue.</li>
                </ul>
              </div>
            </div>
          ) : (
            /* Coding Tab Content */
            <div style={{ position: 'relative', height: '100%', display: 'flex', flexDirection: 'column' }}>
              {/* Proctoring Alerts Overlay */}
              <div className={`proctor-alert warning ${proctorState === 1 ? 'show' : ''}`}>
                <Icons.Eye style={{ width: '16px', height: '16px' }} />
                Tab Switch Detected - 00:12
              </div>
              <div className={`proctor-alert info ${proctorState === 2 ? 'show' : ''}`}>
                <Icons.Shield style={{ width: '16px', height: '16px' }} />
                AI Flag: {pastedCount} lines pasted
              </div>

              {/* Toolbar */}
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 1rem', background: 'rgba(30,41,59,0.3)', borderBottom: '1px solid rgba(51,65,85,0.4)' }}>
                <div className="fca-lang-selector" style={{ padding: '0' }}>
                  <select
                    style={{ background: 'transparent', border: 'none', color: '#e2e8f0', outline: 'none', cursor: 'pointer', padding: '0.375rem 1rem' }}
                    value={selectedLang}
                    onChange={(e) => setSelectedLang(e.target.value)}
                  >
                    {SUPPORTED_LANGUAGES.map(lang => (
                      <option key={lang} value={lang} style={{ background: '#0f1c30' }}>{lang}</option>
                    ))}
                  </select>
                </div>
                <div className="fca-run-actions">
                  <button className="fca-btn-run"><Icons.Play style={{ width: '14px', height: '14px' }} /> Run Tests</button>
                  <button className="fca-btn-submit">Submit Code</button>
                </div>
              </div>

              {/* Code Area */}
              <div className="ide-main" style={{ flex: 1, overflow: 'hidden', position: 'relative' }}>
                <div className="ide-code-area" style={{ paddingTop: '0', overflowY: 'auto', height: '100%', paddingBottom: '2rem', position: 'relative' }}>
                  <div className="ide-line-numbers" style={{ width: '3rem', paddingTop: '1rem' }}>
                    {codeSnippet.map((_, i) => <div key={i}>{i + 1}</div>)}
                  </div>

                  <div className={`ide-code-content ${proctorState === 2 ? 'flash-copy-paste' : ''}`} style={{ paddingTop: '1rem' }}>
                    {codeSnippet.map((line, i) => (
                      <div key={i} style={{ opacity: i < codeIndex ? 1 : 0, transition: 'opacity 0.2s', whiteSpace: 'pre', color: line.includes('def') ? '#60a5fa' : line.includes('return') ? '#c084fc' : line.includes('#') ? '#64748b' : '#cbd5e1' }}>
                        {line}
                        {i === codeIndex - 1 && <span className="fca-cursor"></span>}
                      </div>
                    ))}
                  </div>
                </div>
              </div>



              {/* Test Cases Terminal Window attached to bottom */}
              <div style={{ height: '180px', background: '#0f1c30', borderTop: '1px solid rgba(51, 65, 85, 0.6)', padding: '0.75rem 1rem', overflowY: 'auto' }}>
                <div className="test-status-header">
                  STATUS: <span style={{ color: '#facc15' }}>Running...</span> | Pass: 2 | Hidden: 1
                </div>
                <div className="test-case-row" style={{ padding: '0.5rem', marginBottom: '0.25rem' }}>
                  <div className="test-col-status status-pass"><Icons.CheckCircle style={{ width: '14px', height: '14px' }} /> PASS</div>
                  <div className="test-col-name">Test 1: Simple Graph</div>
                  <div className="test-col-time">12ms</div>
                </div>
                <div className="test-case-row" style={{ padding: '0.5rem', marginBottom: '0.25rem' }}>
                  <div className="test-col-status status-pass"><Icons.CheckCircle style={{ width: '14px', height: '14px' }} /> PASS</div>
                  <div className="test-col-name">Test 2: Graph with Cycles</div>
                  <div className="test-col-time">28ms</div>
                </div>
                <div className="test-case-row" style={{ opacity: 0.7, padding: '0.5rem', marginBottom: '0.25rem' }}>
                  <div className="test-col-status status-hidden"><Icons.Shield style={{ width: '14px', height: '14px' }} /> HIDDEN</div>
                  <div className="test-col-name">Test 3: V=10000 Edge Cases</div>
                  <div className="test-col-time">--</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default function FeatureCodingAssessment() {
  useEffect(() => {
    window.scrollTo(0, 0);
    const appScrollEl = document.querySelector('.app-scroll');
    if (appScrollEl) {
      appScrollEl.scrollTop = 0;
    }
  }, []);

  return (
    <>
      <MainHeader />
      <div className="fca-container">
        {/* Ambient Background Elements */}
        <div className="fca-ambient-bg">
          <div className="fca-glow-1"></div>
          <div className="fca-glow-2"></div>
          <div className="fca-glow-3"></div>
          <div className="bg-grid-pattern"></div>
        </div>

        {/* Split Screen Assessment Hero (Contains both Text and IDE) */}
        <AdvancedSplitScreenMockup />

        {/* Stats Bar & 15 Languages Ticker */}
        <section className="fca-stats-bar">
          <div className="fca-stats-grid">
            <div className="fca-stat-item">
              <div className="fca-stat-num text-gradient">15</div>
              <div className="fca-stat-label">Supported Languages</div>
            </div>
            <div className="fca-stat-item">
              <div className="fca-stat-num text-gradient">100%</div>
              <div className="fca-stat-label">Automated Grading</div>
            </div>
            <div className="fca-stat-item">
              <div className="fca-stat-num text-gradient">Zero</div>
              <div className="fca-stat-label">Environment Setup</div>
            </div>
            <div className="fca-stat-item">
              <div className="fca-stat-num text-gradient">Real-time</div>
              <div className="fca-stat-label">Plagiarism Detection</div>
            </div>
          </div>

          {/* Advanced 15 Languages Infinite Scroll Ticker */}
          <div className="fca-ticker-wrapper">
            <div className="fca-ticker-mask-l"></div>
            <div className="fca-ticker-mask-r"></div>

            <div className="animate-marquee">
              {/* Render the list twice to create a seamless looping effect */}
              {[...SUPPORTED_LANGUAGES, ...SUPPORTED_LANGUAGES].map((lang, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#64748b' }}>
                  <Icons.Code style={{ width: '20px', height: '20px' }} />
                  <span style={{ fontSize: '1.25rem', fontWeight: 'bold', letterSpacing: '0.025em' }}>{lang}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* How it Works (Alternating Layout) */}
        <section className="fca-section" style={{ paddingTop: '6rem', paddingBottom: '6rem' }}>
          <div style={{ textAlign: 'center', maxWidth: '48rem', margin: '0 auto 4rem' }}>
            <h2 style={{ fontSize: '2.25rem', fontWeight: '800', color: '#0F172A', marginBottom: '1.5rem' }}>How It Works</h2>
            <p className="fca-hero-desc" style={{ margin: '0 auto' }}>A seamless, advanced workflow designed to evaluate real-world coding proficiency while ensuring a fantastic candidate experience.</p>
          </div>

          {/* Step 1 */}
          <div className="fca-step">
            <div className="fca-step-content">
              <div className="fca-step-label text-gradient">STEP 01</div>
              <h3 className="fca-step-title">Acurate Custom Challenges</h3>
              <p className="fca-step-desc">
                Choose from our extensive library of algorithmic tasks or build real-world assignments tailored to your exact tech stack. Customize difficulty, time limits, and allowed languages to perfectly match your open role.
              </p>
              <ul className="fca-ul">
                {['Extensive template library', 'Custom codebase support', 'Role-specific scenarios'].map((item, i) => (
                  <li key={i}>
                    <Icons.CheckCircle style={{ width: '20px', height: '20px' }} /> {item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="fca-step-visual">
              <div style={{ background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '1rem', overflow: 'hidden', boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                {/* Mockup Header */}
                <div style={{ backgroundColor: '#F8FAFC', padding: '1rem 1.5rem', borderBottom: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: '600', color: '#0F172A', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Icons.Settings style={{ width: '16px', height: '16px', color: '#3B82F6' }} /> Challenge Setup
                  </span>
                  <div style={{ display: 'flex', gap: '0.25rem' }}>
                    <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#ef4444' }}></div>
                    <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#f59e0b' }}></div>
                    <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#22c55e' }}></div>
                  </div>
                </div>

                {/* Mockup Body */}
                <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                  {/* Title Input */}
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', color: '#64748B', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '600' }}>Challenge Name</label>
                    <div style={{ padding: '0.75rem 1rem', backgroundColor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '0.5rem', color: '#0F172A', fontSize: '0.875rem' }}>
                      Find the Optimal Path (Graph Traversal)
                    </div>
                  </div>

                  {/* Settings Row */}
                  <div style={{ display: 'flex', gap: '1rem' }}>
                    <div style={{ flex: 1 }}>
                      <label style={{ display: 'block', fontSize: '0.75rem', color: '#64748B', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '600' }}>Difficulty</label>
                      <div style={{ padding: '0.5rem 1rem', backgroundColor: '#FEF3C7', border: '1px solid #FBBF24', borderRadius: '0.5rem', color: '#D97706', fontSize: '0.875rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontWeight: '600' }}>
                        Medium
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                      </div>
                    </div>
                    <div style={{ flex: 1 }}>
                      <label style={{ display: 'block', fontSize: '0.75rem', color: '#64748B', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '600' }}>Time Limit</label>
                      <div style={{ padding: '0.5rem 1rem', backgroundColor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '0.5rem', color: '#0F172A', fontSize: '0.875rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontWeight: '500' }}>
                        45 Mins
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                      </div>
                    </div>
                  </div>

                  {/* Languages */}
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', color: '#64748B', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '600' }}>Allowed Languages</label>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <span className="fca-tag" style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)', color: '#2563EB', border: '1px solid rgba(59, 130, 246, 0.3)', display: 'flex', alignItems: 'center' }}>
                        <Icons.CheckCircle style={{ width: '14px', height: '14px', marginRight: '6px' }} /> React
                      </span>
                      <span className="fca-tag" style={{ backgroundColor: 'rgba(234, 179, 8, 0.1)', color: '#D97706', border: '1px solid rgba(234, 179, 8, 0.3)', display: 'flex', alignItems: 'center' }}>
                        <Icons.CheckCircle style={{ width: '14px', height: '14px', marginRight: '6px' }} /> Python
                      </span>
                      <span className="fca-tag" style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)', color: '#059669', border: '1px solid rgba(16, 185, 129, 0.3)', display: 'flex', alignItems: 'center' }}>
                        <Icons.CheckCircle style={{ width: '14px', height: '14px', marginRight: '6px' }} /> Go
                      </span>
                      <span className="fca-tag" style={{ backgroundColor: '#F1F5F9', color: '#64748B', border: '1px dashed #CBD5E1', display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                        + Add Language
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Step 2 (Reversed) */}
          <div className="fca-step reverse">
            <div className="fca-step-content" style={{ paddingLeft: '3rem' }}>
              <div className="fca-step-label text-gradient">STEP 02</div>
              <h3 className="fca-step-title">Seamless Coding Experience</h3>
              <p className="fca-step-desc">
                Candidates code in a clean, intuitive web-based environment equipped with syntax highlighting and clear problem statements. No local environment setup required—they jump straight into solving problems across 15 supported languages.
              </p>
            </div>
            <div className="fca-step-visual">
              <div style={{ background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '1rem', overflow: 'hidden', boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                {/* Header mimicking actual candidate view */}
                <div style={{ backgroundColor: '#F8FAFC', padding: '0.75rem 1rem', borderBottom: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{ display: 'flex', gap: '0.4rem' }}>
                    <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#ef4444' }}></div>
                    <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#f59e0b' }}></div>
                    <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#22c55e' }}></div>
                  </div>
                  <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#3B82F6', borderBottom: '2px solid #3B82F6', paddingBottom: '0.5rem', marginBottom: '-0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Icons.Code style={{width: '14px', height: '14px'}} /> Code Editor
                  </div>
                </div>
                {/* Action Bar */}
                <div style={{ backgroundColor: '#F1F5F9', padding: '0.5rem 1rem', borderBottom: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E2E8F0', padding: '0.25rem 0.75rem', borderRadius: '0.375rem', color: '#475569', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    Python <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
                  </div>
                  <div style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)', color: '#2563EB', border: '1px solid rgba(59, 130, 246, 0.3)', padding: '0.25rem 0.75rem', borderRadius: '0.375rem', fontSize: '0.75rem', fontWeight: '600' }}>
                    Run Tests
                  </div>
                </div>
                {/* Code Area */}
                <div style={{ padding: '1rem', backgroundColor: '#0d1117', fontFamily: 'monospace', fontSize: '0.875rem', color: '#cbd5e1', lineHeight: '1.6', position: 'relative' }}>
                  <div style={{display: 'flex', gap: '1rem'}}>
                    <div style={{color: '#475569', userSelect: 'none', textAlign: 'right'}}>
                      1<br/>2<br/>3<br/>4<br/>5<br/>6
                    </div>
                    <div>
                      <div><span style={{ color: '#c084fc' }}>def</span> <span style={{ color: '#60a5fa' }}>find_optimal_path</span>(graph, start, end):</div>
                      <div style={{ paddingLeft: '1rem' }}>open_set = [(<span style={{color: '#f59e0b'}}>0</span>, start)]</div>
                      <div style={{ paddingLeft: '1rem' }}>came_from = {'{}'}</div>
                      <div style={{ paddingLeft: '1rem' }}><span style={{ color: '#c084fc' }}>while</span> open_set:</div>
                      <div style={{ paddingLeft: '2rem' }}>current = heapq.heappop(open_set)[<span style={{color: '#f59e0b'}}>1</span>]</div>
                      <div style={{ paddingLeft: '2rem', color: '#475569' }}># Add core logic</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Step 3 */}
          <div className="fca-step">
            <div className="fca-step-content">
              <div className="fca-step-label text-gradient">STEP 03</div>
              <h3 className="fca-step-title">Automated Test Execution</h3>
              <p className="fca-step-desc">
                Code is instantly evaluated against visible and hidden test cases. We analyze not just for correctness, but also for time and space complexity, giving you deep, data-driven insights into code efficiency.
              </p>
            </div>
            <div className="fca-step-visual">
              <div style={{ background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '1rem', padding: '1.5rem', boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', borderRadius: '0.75rem', backgroundColor: '#F0FDF4', border: '1px solid #BBF7D0' }}>
                    <div style={{ display: 'flex', alignItems: 'center' }}><Icons.CheckCircle style={{ width: '20px', height: '20px', color: '#16A34A', marginRight: '0.75rem' }} /> <span style={{ color: '#15803D', fontWeight: '500', fontSize: '0.875rem' }}>Test 1: Boundary Conditions</span></div>
                    <span style={{ color: '#16A34A', fontFamily: 'monospace', fontSize: '0.75rem', fontWeight: '700' }}>24ms</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', borderRadius: '0.75rem', backgroundColor: '#F0FDF4', border: '1px solid #BBF7D0' }}>
                    <div style={{ display: 'flex', alignItems: 'center' }}><Icons.CheckCircle style={{ width: '20px', height: '20px', color: '#16A34A', marginRight: '0.75rem' }} /> <span style={{ color: '#15803D', fontWeight: '500', fontSize: '0.875rem' }}>Test 2: Large Dataset (O(n log n))</span></div>
                    <span style={{ color: '#16A34A', fontFamily: 'monospace', fontSize: '0.75rem', fontWeight: '700' }}>112ms</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', borderRadius: '0.75rem', backgroundColor: '#EFF6FF', border: '1px solid #BFDBFE' }}>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <span style={{ width: '20px', height: '20px', marginRight: '0.75rem', borderRadius: '50%', border: '2px solid #BFDBFE', borderTopColor: '#3B82F6' }} className="animate-spin"></span>
                      <span style={{ color: '#1E40AF', fontWeight: '500', fontSize: '0.875rem' }}>Test 3: Hidden Edge Cases</span>
                    </div>
                    <span style={{ color: '#3B82F6', fontFamily: 'monospace', fontSize: '0.75rem', fontWeight: '700' }} className="animate-pulse">Running...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Step 4 (Reversed) */}
          <div className="fca-step reverse">
            <div className="fca-step-content" style={{ paddingLeft: '3rem' }}>
              <div className="fca-step-label text-gradient-purple">STEP 04</div>
              <h3 className="fca-step-title">Keystroke & Behavior Analysis</h3>
              <p className="fca-step-desc">
                Go beyond the final code. Our platform analyzes candidate behavior in real-time, providing a detailed report on keystroke latency, coding patterns, and automatically flagging suspicious copy-paste activity to ensure complete integrity.
              </p>
            </div>
            <div className="fca-step-visual">
              <div style={{ background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '1rem', overflow: 'hidden', boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                <div style={{ backgroundColor: '#F8FAFC', padding: '1rem 1.5rem', borderBottom: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: '600', color: '#0F172A', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Icons.Shield style={{ width: '16px', height: '16px', color: '#8B5CF6' }} /> Behavioral Report
                  </span>
                  <div style={{ fontSize: '0.75rem', fontWeight: '700', backgroundColor: '#FEF2F2', color: '#DC2626', padding: '0.25rem 0.5rem', borderRadius: '0.25rem', border: '1px solid #FECACA' }}>
                    High Risk Flagged
                  </div>
                </div>
                
                <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div style={{ backgroundColor: '#F0FDF4', padding: '1rem', borderRadius: '0.5rem', border: '1px solid #BBF7D0' }}>
                      <div style={{ fontSize: '0.75rem', color: '#64748B', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Avg. Keystroke Latency</div>
                      <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#0F172A' }}>240<span style={{ fontSize: '0.875rem', color: '#64748B', marginLeft: '0.25rem' }}>ms</span></div>
                      <div style={{ fontSize: '0.75rem', color: '#16A34A', marginTop: '0.25rem' }}>Natural typing speed</div>
                    </div>
                    <div style={{ backgroundColor: '#FEF2F2', padding: '1rem', borderRadius: '0.5rem', border: '1px solid #FECACA' }}>
                      <div style={{ fontSize: '0.75rem', color: '#64748B', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Pasted Blocks</div>
                      <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#DC2626' }}>3</div>
                      <div style={{ fontSize: '0.75rem', color: '#DC2626', marginTop: '0.25rem' }}>Suspicious activity</div>
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#0F172A', marginBottom: '0.75rem' }}>Detected Anomalies</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', backgroundColor: '#FEF2F2', padding: '0.75rem', borderRadius: '0.5rem', borderLeft: '2px solid #EF4444' }}>
                        <div style={{ marginTop: '0.125rem', color: '#EF4444', fontSize: '1.25rem', lineHeight: '1' }}>⚠</div>
                        <div>
                          <div style={{ fontSize: '0.875rem', color: '#0F172A', fontWeight: '500' }}>Massive Code Insertion</div>
                          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>42 lines pasted simultaneously at 12:04 PM.</div>
                        </div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', backgroundColor: '#FFFBEB', padding: '0.75rem', borderRadius: '0.5rem', borderLeft: '2px solid #F59E0B' }}>
                        <div style={{ marginTop: '0.125rem', color: '#F59E0B', fontSize: '1.25rem', lineHeight: '1' }}>⚡</div>
                        <div>
                          <div style={{ fontSize: '0.875rem', color: '#0F172A', fontWeight: '500' }}>Erratic Typing Patterns</div>
                          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Keystroke latency dropped from 240ms to 40ms.</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Security & Proctoring Highlight */}
        <section className="fca-security">
          <div className="fca-grid-2">
            <div>
              <div className="fca-security-icon">
                <Icons.Shield style={{ width: '40px', height: '40px', color: '#f87171' }} />
              </div>
              <h2 className="fca-step-title" style={{ fontSize: '2.25rem' }}>Enterprise-Grade Security & Proctoring</h2>
              <p className="fca-step-desc" style={{ marginBottom: '2rem' }}>
                Maintain the highest level of assessment integrity. Our non-intrusive yet highly effective proctoring suite ensures that the skills you see are the skills you get.
              </p>
            </div>

            <div className="fca-grid-features">
              {[
                { title: "Tab-Tracking", desc: "Alerts and logs instances when candidates navigate away from the assessment window." },
                { title: "Code Similarity Checks", desc: "Advanced AST (Abstract Syntax Tree) comparison against a vast database to detect plagiarism." },
                { title: "Passive Webcam Proctoring", desc: "Optional periodic snapshots to verify candidate identity without intrusive live monitoring." },
                { title: "Copy-Paste Restrictions", desc: "Configurable settings to disable or flag heavy copy-pasting from external sources." },
                { title: "Typing Speed Analytics", desc: "Monitors keystroke latency to differentiate between natural typing speeds and automated code injection." },
                { title: "Behavior Pattern Recognition", desc: "Identifies erratic coding behaviors to flag potential instances of cheating or unauthorized assistance." }
              ].map((feature, idx) => (
                <div key={idx} className="glass-card" style={{ padding: '1.5rem', borderRadius: '0.75rem' }}>
                  <h4 className="fca-feature-title">{feature.title}</h4>
                  <p className="fca-feature-desc">{feature.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="shared-cta-section">
          <div className="shared-cta-card">
            <div className="shared-cta-badge">
              <span>Real-time Execution</span>
            </div>
            <h2 className="shared-cta-title">Ready to build a world-class engineering team?</h2>
            <p className="shared-cta-text">
              Join leading tech companies who trust VerifiHireAI to identify and hire top developer talent faster and more accurately.
            </p>
            <Link to="/contact" className="shared-cta-btn">
              Get Started For Free
            </Link>
          </div>
        </section>
      </div>
      <Footer />
    </>
  );
}