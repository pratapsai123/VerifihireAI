from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "Which command is used to download the provider plugins required for a Terraform configuration?",
    "options": {
      "A": "terraform plan",
      "B": "terraform init",
      "C": "terraform get",
      "D": "terraform download"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary purpose of the 'Terraform State' file (terraform.tfstate)?",
    "options": {
      "A": "To act as a backup of your HCL code.",
      "B": "To store the mapping between your configuration and the real-world resources provisioned in the cloud.",
      "C": "To store your cloud provider credentials securely.",
      "D": "To list all available modules in the Terraform Registry."
    },
    "answer": "B"
  },
  {
    "question": "Which file extension is standard for Terraform configuration files?",
    "options": {
      "A": ".tfconf",
      "B": ".tf",
      "C": ".hcl",
      "D": ".yaml"
    },
    "answer": "B"
  },
  {
    "question": "In HCL, which block type is used to query information from a cloud provider without creating a new resource?",
    "options": {
      "A": "resource",
      "B": "variable",
      "C": "data",
      "D": "output"
    },
    "answer": "C"
  },
  {
    "question": "What does 'Idempotency' mean in the context of Terraform?",
    "options": {
      "A": "Terraform will create a new resource every time 'apply' is run.",
      "B": "Running the same configuration multiple times results in the same infrastructure state without unintended side effects.",
      "C": "Terraform can only manage one cloud provider at a time.",
      "D": "The configuration is automatically converted to JSON."
    },
    "answer": "B"
  },
  {
    "question": "Which command would you use to see a preview of the changes Terraform will make to your infrastructure?",
    "options": {
      "A": "terraform show",
      "B": "terraform plan",
      "C": "terraform validate",
      "D": "terraform verify"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Terraform Provider'?",
    "options": {
      "A": "A cloud platform like AWS or Azure.",
      "B": "A plugin that translates Terraform HCL code into API calls for a specific service or platform.",
      "C": "A person who writes Terraform code.",
      "D": "A remote server that stores the state file."
    },
    "answer": "B"
  },
  {
    "question": "How do you define a variable in Terraform so that its value can be passed during execution?",
    "options": {
      "A": "Using the 'locals' block.",
      "B": "Using the 'variable' block.",
      "C": "Defining it in a .txt file.",
      "D": "Using the 'output' block."
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'terraform fmt' command?",
    "options": {
      "A": "To check for syntax errors in your code.",
      "B": "To automatically rewrite configuration files to a canonical format and style.",
      "C": "To convert .tf files into JSON.",
      "D": "To delete unused resources."
    },
    "answer": "B"
  },
  {
    "question": "True or False: Terraform is a 'declarative' tool, meaning you describe the desired end-state rather than the step-by-step instructions to reach it.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which argument is used to create an explicit dependency between two resources in Terraform?",
    "options": {
      "A": "required_by",
      "B": "depends_on",
      "C": "after",
      "D": "links_to"
    },
    "answer": "B"
  },
  {
    "question": "What is the default name for the file that automatically provides values for variables in a directory?",
    "options": {
      "A": "vars.tf",
      "B": "terraform.tfvars",
      "C": "config.yaml",
      "D": "values.tf"
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to remove all resources managed by a specific Terraform configuration?",
    "options": {
      "A": "terraform delete",
      "B": "terraform destroy",
      "C": "terraform remove",
      "D": "terraform clean"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'terraform validate' command check?",
    "options": {
      "A": "If the cloud resources actually exist.",
      "B": "The syntax of the configuration files and the consistency of the attributes.",
      "C": "If the state file is locked.",
      "D": "If the user has permission to delete resources."
    },
    "answer": "B"
  },
  {
    "question": "In a team environment, what is the best practice for storing the Terraform state file?",
    "options": {
      "A": "Commit it to your Git repository.",
      "B": "Use a 'Remote Backend' like AWS S3 or Terraform Cloud with state locking enabled.",
      "C": "Keep it on a shared local network drive.",
      "D": "Email it to your teammates after every change."
    },
    "answer": "B"
  },
  {
    "question": "Which backend type is required to enable State Locking when using Amazon S3 as a remote backend?",
    "options": {
      "A": "Redis",
      "B": "DynamoDB",
      "C": "CloudWatch",
      "D": "IAM Policy"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary benefit of using Terraform Modules?",
    "options": {
      "A": "They make the code run faster.",
      "B": "They allow you to package and reuse resource configurations, promoting the DRY (Don't Repeat Yourself) principle.",
      "C": "They automatically encrypt the state file.",
      "D": "They eliminate the need for a provider block."
    },
    "answer": "B"
  },
  {
    "question": "In HCL, how do you access an output value named 'instance_ip' from a module named 'web_server'?",
    "options": {
      "A": "module.web_server.instance_ip",
      "B": "module.instance_ip.web_server",
      "C": "web_server.output.instance_ip",
      "D": "module.web_server.outputs.instance_ip"
    },
    "answer": "A"
  },
  {
    "question": "What does the 'terraform state rm' command do?",
    "options": {
      "A": "Deletes the physical resource from the cloud provider.",
      "B": "Removes a resource from the Terraform state file without destroying the actual infrastructure.",
      "C": "Removes the entire .terraform directory.",
      "D": "Clears the local cache of provider plugins."
    },
    "answer": "B"
  },
  {
    "question": "Which meta-argument is used to create multiple instances of a resource based on a list or map of strings?",
    "options": {
      "A": "count",
      "B": "for_each",
      "C": "loop",
      "D": "repeat"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Terraform Workspaces'?",
    "options": {
      "A": "To allow multiple users to edit the same .tf file simultaneously.",
      "B": "To manage multiple distinct states for the same configuration (e.g., Dev vs. Prod) within the same backend.",
      "C": "To organize local folders on your computer.",
      "D": "To provide a GUI for the Terraform CLI."
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to manually mark a resource for recreation during the next apply because it is corrupted or out of sync?",
    "options": {
      "A": "terraform refresh",
      "B": "terraform taint (or terraform apply -replace)",
      "C": "terraform recreate",
      "D": "terraform mark"
    },
    "answer": "B"
  },
  {
    "question": "In a Terraform module, where should the 'source' argument be defined?",
    "options": {
      "A": "Inside the resource block.",
      "B": "Inside the module block.",
      "C": "In the terraform block.",
      "D": "In the variable definition."
    },
    "answer": "B"
  },
  {
    "question": "What happens if you run 'terraform plan' and a resource exists in the state file but has been manually deleted in the cloud console?",
    "options": {
      "A": "Terraform throws an error and stops.",
      "B": "Terraform detects the drift and proposes to recreate the resource to match the configuration.",
      "C": "Terraform deletes the entry from the state file and does nothing.",
      "D": "Terraform ignores the change."
    },
    "answer": "B"
  },
  {
    "question": "Which HCL function is used to merge multiple maps into a single map?",
    "options": {
      "A": "combine()",
      "B": "merge()",
      "C": "join()",
      "D": "concat()"
    },
    "answer": "B"
  },
  {
    "question": "True or False: A 'Local-only' module can be sourced by providing a relative path starting with './' or '../'.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Sensitive' argument in a variable block used for?",
    "options": {
      "A": "To encrypt the variable value in the .tf file.",
      "B": "To prevent the value from being displayed in the console output during plan or apply.",
      "C": "To hide the variable from other developers in Git.",
      "D": "To make the variable read-only."
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'terraform.lock.hcl' file?",
    "options": {
      "A": "To prevent multiple users from running Terraform apply.",
      "B": "To record the specific versions and hashes of providers used, ensuring consistent builds across different environments.",
      "C": "To store encrypted passwords.",
      "D": "To lock the state file in S3."
    },
    "answer": "B"
  },
  {
    "question": "Which meta-argument allows you to dynamically construct nested blocks within a resource based on a complex variable?",
    "options": {
      "A": "nested_block",
      "B": "dynamic",
      "C": "iterator",
      "D": "content"
    },
    "answer": "B"
  },
  {
    "question": "What does 'External Data Source' allow Terraform to do?",
    "options": {
      "A": "Connect to an external SQL database.",
      "B": "Execute an external script (like Python or Bash) and use its JSON output as a data source in Terraform.",
      "C": "Download files from the internet.",
      "D": "Import resources from a different cloud provider."
    },
    "answer": "B"
  },
  {
    "question": "In Terraform Cloud, what is the 'VCS-driven workflow'?",
    "options": {
      "A": "Manually uploading .tfstate files to GitHub.",
      "B": "A workflow where a commit to a linked version control repository (like GitHub or GitLab) automatically triggers a Terraform plan and apply.",
      "C": "Using Git commands to provision cloud resources directly.",
      "D": "A system that prevents developers from using branches."
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'lifecycle' block's 'prevent_destroy' argument?",
    "options": {
      "A": "It makes the resource immortal even if you delete the cloud account.",
      "B": "It causes Terraform to reject any plan that would result in the destruction of the resource (e.g., accidental deletion of a production database).",
      "C": "It prevents the resource from being updated.",
      "D": "It forces the resource to stay at the current version forever."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Sentinel' in the context of Terraform Enterprise?",
    "options": {
      "A": "A monitoring tool for CPU usage.",
      "B": "A Policy-as-Code framework that allows organizations to define and enforce logic-based guardrails (e.g., 'no instances without tags').",
      "C": "A specialized provider for security groups.",
      "D": "The service that handles state locking."
    },
    "answer": "B"
  },
  {
    "question": "Which command allows you to bring a resource created outside of Terraform (via the UI or CLI) under Terraform management?",
    "options": {
      "A": "terraform fetch",
      "B": "terraform import",
      "C": "terraform adopt",
      "D": "terraform pull"
    },
    "answer": "B"
  },
  {
    "question": "In a 'lifecycle' block, what does 'create_before_destroy' achieve?",
    "options": {
      "A": "It creates a backup of the resource before deleting it.",
      "B": "It ensures that a replacement resource is fully provisioned and functional before the old resource is deleted, minimizing downtime.",
      "C": "It doubles the cost of the resource.",
      "D": "It skips the destruction phase entirely."
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Terraform Private Module Registry'?",
    "options": {
      "A": "A list of modules hidden from the public internet.",
      "B": "An internal repository within Terraform Cloud/Enterprise for sharing verified, standardized infrastructure components across an organization.",
      "C": "A way to encrypt module code on a local disk.",
      "D": "A marketplace where you can buy modules with crypto."
    },
    "answer": "B"
  },
  {
    "question": "Which command is used to move a resource to a different address in the state file (e.g., when refactoring a resource into a module)?",
    "options": {
      "A": "terraform state mv",
      "B": "terraform state cp",
      "C": "terraform state migrate",
      "D": "terraform state push"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'moved' block introduced in Terraform 1.1?",
    "options": {
      "A": "A way to move the office location of your servers.",
      "B": "A declarative way to record resource refactoring (renames or moving into modules) so that state migration happens automatically for all users.",
      "C": "A block that deletes old code automatically.",
      "D": "A way to transfer resources between cloud providers."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Speculative Plans' in Terraform Cloud allow developers to see the impact of their changes on a Pull Request without actually having permission to apply them.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "In HCL, what is a 'Splat Expression' (*)?",
    "options": {
      "A": "A way to multiply numbers.",
      "B": "A concise way to extract a list of values from a specific attribute across all instances of a resource (e.g., aws_instance.web[*].id).",
      "C": "A wildcard for provider versions.",
      "D": "A command that deletes all resources in a region."
    },
    "answer": "B"
  },
  {
    "question": "Which environment variable can be used to enable detailed debug logging in Terraform?",
    "options": {
      "A": "TF_DEBUG",
      "B": "TF_LOG",
      "C": "TERRAFORM_VERBOSE",
      "D": "TRACE_TF"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Partial Configuration' in the context of Terraform Backends?",
    "options": {
      "A": "A configuration that is missing half of its resources.",
      "B": "Omitting certain backend arguments (like secrets) from the code and providing them via a file or command line during 'terraform init'.",
      "C": "A backend that only works for certain regions.",
      "D": "A way to run Terraform without a state file."
    },
    "answer": "B"
  },
  {
    "question": "What is the role of 'Run Triggers' in Terraform Cloud?",
    "options": {
      "A": "To start a fire in the data center.",
      "B": "To create a dependency between workspaces, so that a successful apply in one workspace triggers a plan in another.",
      "C": "To alert the security team when a plan is run.",
      "D": "To automatically retry failed applies."
    },
    "answer": "B"
  },
  {
    "question": "What happens if you use the 'ignore_changes' lifecycle argument for a specific attribute?",
    "options": {
      "A": "Terraform will delete that attribute.",
      "B": "Terraform will ignore any drift or manual changes to that attribute in the cloud, preventing it from being 'corrected' back to the HCL value.",
      "C": "Terraform will stop tracking the resource entirely.",
      "D": "The attribute becomes read-only in the cloud console."
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Terraform Provider SDK'?",
    "options": {
      "A": "A manual for using AWS with Terraform.",
      "B": "A set of Go libraries used by developers to build and maintain custom Terraform providers.",
      "C": "A tool that converts Python to HCL.",
      "D": "The cloud console for HashiCorp."
    },
    "answer": "B"
  },
  {
    "question": "What is Terraform primarily used for?",
    "options": {
      "A": "Application development",
      "B": "Infrastructure as Code",
      "C": "Container orchestration",
      "D": "CI/CD pipelines"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Terraform is developed by HashiCorp.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO cloud providers are supported by Terraform?",
    "options": {
      "A": "AWS",
      "B": "Azure",
      "C": "Photoshop",
      "D": "Excel"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What language is used to write Terraform configurations?",
    "options": {
      "A": "YAML",
      "B": "JSON",
      "C": "HCL",
      "D": "XML"
    },
    "answer": "C"
  },
  {
    "question": "True or False: Terraform configuration files typically use the .tf extension.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does `terraform init` do?",
    "options": {
      "A": "Applies infrastructure changes",
      "B": "Initializes the working directory",
      "C": "Deletes resources",
      "D": "Formats code"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO actions are performed by `terraform init`?",
    "options": {
      "A": "Download providers",
      "B": "Configure backend",
      "C": "Create resources",
      "D": "Destroy state"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: `terraform init` must be run before `terraform plan`.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of `terraform plan`?",
    "options": {
      "A": "Apply changes immediately",
      "B": "Show execution plan",
      "C": "Delete infrastructure",
      "D": "Validate syntax only"
    },
    "answer": "B"
  },
  {
    "question": "True or False: `terraform plan` modifies infrastructure.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which command actually creates or updates infrastructure?",
    "options": {
      "A": "terraform validate",
      "B": "terraform plan",
      "C": "terraform apply",
      "D": "terraform fmt"
    },
    "answer": "C"
  },
  {
    "question": "Which TWO files can store Terraform state?",
    "options": {
      "A": "terraform.tfstate",
      "B": "Remote backend",
      "C": "variables.tf",
      "D": "outputs.tf"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Terraform state maps resources to real infrastructure.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a Terraform provider?",
    "options": {
      "A": "A cloud region",
      "B": "A plugin that interacts with APIs",
      "C": "A backend type",
      "D": "A variable file"
    },
    "answer": "B"
  },
  {
    "question": "Which block defines a provider?",
    "options": {
      "A": "resource",
      "B": "provider",
      "C": "module",
      "D": "output"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Terraform can manage only cloud resources.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is a resource in Terraform?",
    "options": {
      "A": "A configuration file",
      "B": "An infrastructure object",
      "C": "A provider plugin",
      "D": "A state file"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are valid Terraform resource attributes?",
    "options": {
      "A": "count",
      "B": "depends_on",
      "C": "runtime",
      "D": "compile"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: `count` allows creating multiple instances of a resource.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does `depends_on` do?",
    "options": {
      "A": "Deletes dependent resources",
      "B": "Defines explicit resource dependencies",
      "C": "Sets provider version",
      "D": "Stores state"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO data types are supported in Terraform variables?",
    "options": {
      "A": "string",
      "B": "number",
      "C": "binary",
      "D": "pointer"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Variables can have default values.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of `terraform destroy`?",
    "options": {
      "A": "Remove state file only",
      "B": "Delete managed infrastructure",
      "C": "Remove providers",
      "D": "Clear variables"
    },
    "answer": "B"
  },
  {
    "question": "True or False: `terraform destroy` requires confirmation by default.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary advantage of using the 'moved' block over the 'terraform state mv' command?",
    "options": {
      "A": "It executes faster during the apply phase.",
      "B": "It provides a declarative, version-controlled record of refactoring that automatically migrates state for all team members.",
      "C": "It allows moving resources between different cloud providers.",
      "D": "It encrypts the resource address in the state file."
    },
    "answer": "B"
  },
  {
    "question": "In Terraform 1.10+, what is the purpose of 'Terraform Stacks' (currently in preview/beta)?",
    "options": {
      "A": "To stack multiple physical servers on top of each other.",
      "B": "To manage complex, multi-environment deployments as a single unit, handling cross-workspace dependencies and orchestration natively.",
      "C": "To replace the HCL language with a Python-based stack.",
      "D": "To provide a way to 'stack' multiple state files into a single .tfstate file."
    },
    "answer": "B"
  },
  {
    "question": "When developing a custom provider, why is the 'Terraform Plugin Framework' now recommended over the older 'SDKv2'?",
    "options": {
      "A": "SDKv2 is no longer supported by HashiCorp.",
      "B": "The Framework supports modern Go patterns, provides better data access, and handles 'null' and 'unknown' values more robustly.",
      "C": "The Framework is written in Rust, making it 10x faster.",
      "D": "The Framework is the only way to support AWS resources."
    },
    "answer": "B"
  },
  {
    "question": "What does the 'validation' block inside a variable definition allow you to do?",
    "options": {
      "A": "Check if the user has a valid credit card.",
      "B": "Define custom logic and error messages to ensure input variables meet specific criteria (e.g., regex for naming conventions) before the plan runs.",
      "C": "Automatically fix typos in the variable values.",
      "D": "Check if the cloud provider has enough capacity for the resource."
    },
    "answer": "B"
  },
  {
    "question": "How does 'Optional Object Attributes' (introduced in 1.3) simplify module design?",
    "options": {
      "A": "It makes all resources in a module optional.",
      "B": "It allows developers to define complex object variables where some fields can be omitted by the caller without requiring manual default value setting for every field.",
      "C": "It reduces the cost of the module by 50%.",
      "D": "It allows the model to skip the 'plan' phase."
    },
    "answer": "B"
  },
  {
    "question": "True or False: The 'check' block (v1.5+) allows for continuous validation of infrastructure health *after* deployment, without affecting the resource lifecycle itself.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "In the context of 'Preconditions' and 'Postconditions', what happens if a 'postcondition' block fails during an apply?",
    "options": {
      "A": "Terraform ignores the failure and continues.",
      "B": "Terraform halts the apply and marks the resource as 'tainted' because the system's final state did not meet the specified criteria.",
      "C": "Terraform automatically rolls back all changes in the account.",
      "D": "The resource is deleted immediately."
    },
    "answer": "B"
  },
  {
    "question": "What is 'Protocol Version 6' in the context of Terraform Providers?",
    "options": {
      "A": "A new version of the HTTP protocol.",
      "B": "The latest gRPC-based communication protocol between the Terraform Core and plugins, enabling features like nested attributes.",
      "C": "The version of HCL used for security groups.",
      "D": "The 6th iteration of the AWS provider."
    },
    "answer": "B"
  },
  {
    "question": "When should you use a 'null_resource' combined with a 'trigger' in modern Terraform?",
    "options": {
      "A": "To save money by not creating any resources.",
      "B": "To execute provisioners or arbitrary actions only when a specific set of values changes, effectively creating a 'reactive' script execution.",
      "C": "When you want to delete the state file.",
      "D": "To act as a placeholder for an image."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Continuous Drift Detection' in Terraform Cloud/Enterprise uses a 'speculative plan' to alert you if your real-world infrastructure no longer matches your code.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a Terraform module?",
    "options": {
      "A": "A provider plugin",
      "B": "A reusable collection of Terraform configurations",
      "C": "A state backend",
      "D": "A single resource"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Every Terraform configuration is itself a module.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO types of modules exist in Terraform?",
    "options": {
      "A": "Root module",
      "B": "Child module",
      "C": "Remote module",
      "D": "Binary module"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "How do you reference a child module output?",
    "options": {
      "A": "var.output_name",
      "B": "module.<name>.<output>",
      "C": "output.<name>",
      "D": "data.<name>"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Modules help enforce DRY (Don’t Repeat Yourself) principles.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a Terraform backend?",
    "options": {
      "A": "Execution engine",
      "B": "State storage configuration",
      "C": "Provider configuration",
      "D": "Resource dependency graph"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO are common remote backends?",
    "options": {
      "A": "S3",
      "B": "Terraform Cloud",
      "C": "GitHub",
      "D": "Docker"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Using a remote backend enables team collaboration.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is state locking?",
    "options": {
      "A": "Encrypting state files",
      "B": "Preventing concurrent state modifications",
      "C": "Versioning providers",
      "D": "Freezing variables"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO backends support state locking?",
    "options": {
      "A": "S3 with DynamoDB",
      "B": "Terraform Cloud",
      "C": "Local backend",
      "D": "JSON backend"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: State locking prevents race conditions.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a Terraform workspace?",
    "options": {
      "A": "Separate execution environment with its own state",
      "B": "A provider alias",
      "C": "A module version",
      "D": "A variable file"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO use cases fit Terraform workspaces?",
    "options": {
      "A": "Multiple environments (dev/prod)",
      "B": "Feature testing",
      "C": "Provider upgrades",
      "D": "Code formatting"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Workspaces share the same state file.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is a data source in Terraform?",
    "options": {
      "A": "A mutable resource",
      "B": "A read-only lookup for existing infrastructure",
      "C": "A state backend",
      "D": "A module output"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO examples are valid data sources?",
    "options": {
      "A": "aws_ami",
      "B": "aws_vpc",
      "C": "terraform_state",
      "D": "provider_config"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Data sources can create infrastructure.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What does `terraform validate` do?",
    "options": {
      "A": "Checks syntax and internal consistency",
      "B": "Applies changes",
      "C": "Downloads providers",
      "D": "Destroys resources"
    },
    "answer": "A"
  },
  {
    "question": "True or False: `terraform validate` requires provider credentials.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What does `terraform fmt` do?",
    "options": {
      "A": "Formats Terraform configuration files",
      "B": "Validates state",
      "C": "Optimizes execution",
      "D": "Encrypts variables"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO benefits does formatting provide?",
    "options": {
      "A": "Consistency",
      "B": "Readability",
      "C": "Lower costs",
      "D": "Faster applies"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: `terraform fmt` modifies .tf files.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a provider alias?",
    "options": {
      "A": "Duplicate provider",
      "B": "Named provider configuration",
      "C": "Module version",
      "D": "State snapshot"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Provider aliases allow multi-region deployments.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Introduced in Terraform 1.10, what is the 'primary' characteristic of an 'ephemeral' resource block?",
    "options": {
      "A": "It automatically deletes itself after 24 hours.",
      "B": "It is never persisted in the Terraform state file or plan artifacts, making it ideal for handling sensitive data like temporary credentials.",
      "C": "It can only be used with the AWS provider.",
      "D": "It runs only during the 'terraform destroy' phase."
    },
    "answer": "B"
  },
  {
    "question": "What happens if an ephemeral resource references an input that is 'unknown' during the plan phase (e.g., an ID from a resource being created)?",
    "options": {
      "A": "Terraform throws a 'Value Unknown' error and halts.",
      "B": "Terraform defers the execution (opening) of that ephemeral resource until the apply stage.",
      "C": "Terraform uses a placeholder 'mock' value.",
      "D": "The ephemeral resource is skipped entirely."
    },
    "answer": "B"
  },
  {
    "question": "In Terraform Stacks (GA 2026), what is a 'Deployment'?",
    "options": {
      "A": "A single instance of a resource.",
      "B": "A specific instantiation of a Stack configuration with a unique set of inputs (e.g., 'staging' vs 'production'), managed as a coordinated unit.",
      "C": "The command that replaced 'terraform apply'.",
      "D": "A backup of the state file."
    },
    "answer": "B"
  },
  {
    "question": "What is the role of the 'check' block introduced in later Terraform versions?",
    "options": {
      "A": "To verify the syntax of the HCL code.",
      "B": "To define functional assertions that run after every apply/plan to verify infrastructure health without affecting the resource lifecycle.",
      "C": "To check the developer's cloud billing limit.",
      "D": "To force a manual approval step."
    },
    "answer": "B"
  },
  {
    "question": "True or False: 'Deferred Actions' allow providers to perform side-effects (like triggering a backup or clearing a cache) that are tied to resource lifecycle events but do not manage persistent state.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which framework is now the official standard for developing new Terraform providers as of 2026, offering better support for 'null' vs 'unknown' values?",
    "options": {
      "A": "Terraform Plugin SDKv2",
      "B": "Terraform Plugin Framework",
      "C": "Terraform Provider Kit (TPK)",
      "D": "Go-Cloud-IaC"
    },
    "answer": "B"
  },
  {
    "question": "What does the 'terraform stacks providers-lock' command do?",
    "options": {
      "A": "Prevents other users from editing providers.",
      "B": "Writes out the dependency locks for all providers configured within a Stack's components.",
      "C": "Encrypts the provider credentials.",
      "D": "Checks if the providers are compatible with the cloud region."
    },
    "answer": "B"
  },
  {
    "question": "In a 'removed' block (introduced to replace manual state rm), what does the 'destroy = false' argument achieve?",
    "options": {
      "A": "It prevents the resource from ever being deleted.",
      "B": "It tells Terraform to stop managing the resource and remove it from state, but keep the actual resource running in the cloud.",
      "C": "It marks the resource as corrupted.",
      "D": "It forces a 'destroy' even if the resource is busy."
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Terraform MCP Server' used for in the 2026 ecosystem?",
    "options": {
      "A": "Connecting Minecraft servers to the cloud.",
      "B": "A Model Context Protocol server that allows AI agents to interact directly with Terraform configurations, registries, and state for validated automation.",
      "C": "A specialized proxy for multi-cloud networking.",
      "D": "A hardware appliance for local state storage."
    },
    "answer": "B"
  },
  {
    "question": "How does 'Resource Identity' (v1.12+) improve bulk imports in HCP Terraform?",
    "options": {
      "A": "By automatically generating random names for resources.",
      "B": "By using a centralized identity search to discover unmanaged cloud resources and map them to import blocks automatically.",
      "C": "By requiring a biometric scan from the developer.",
      "D": "By moving all resources to a single global region."
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the `lifecycle` block in Terraform?",
    "options": {
      "A": "Control provider versions",
      "B": "Customize resource behavior",
      "C": "Manage backend state",
      "D": "Encrypt variables"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO lifecycle arguments are commonly used?",
    "options": {
      "A": "create_before_destroy",
      "B": "ignore_changes",
      "C": "depends_on",
      "D": "count"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: `create_before_destroy` helps reduce downtime.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does `ignore_changes` do?",
    "options": {
      "A": "Ignores resource creation",
      "B": "Prevents Terraform from updating specified attributes",
      "C": "Skips validation",
      "D": "Ignores provider errors"
    },
    "answer": "B"
  },
  {
    "question": "What is `for_each` used for?",
    "options": {
      "A": "Iterating over resources",
      "B": "Looping over providers",
      "C": "Repeating modules only",
      "D": "Parallel execution"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO collection types can be used with `for_each`?",
    "options": {
      "A": "map",
      "B": "set",
      "C": "list",
      "D": "string"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: `count` and `for_each` can be used together on the same resource.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is a Terraform provisioner?",
    "options": {
      "A": "Cloud API plugin",
      "B": "Tool to execute scripts on resources",
      "C": "State backend",
      "D": "Variable type"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO provisioners are built into Terraform?",
    "options": {
      "A": "file",
      "B": "local-exec",
      "C": "docker",
      "D": "ssh"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: HashiCorp recommends avoiding provisioners when possible.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is a Terraform variable sensitivity flag used for?",
    "options": {
      "A": "Encryption",
      "B": "Hiding values in CLI output",
      "C": "Validation",
      "D": "Version control"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Sensitive variables are encrypted in state by default.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO methods can supply variable values?",
    "options": {
      "A": "terraform.tfvars",
      "B": "Environment variables",
      "C": "outputs.tf",
      "D": "providers.tf"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What does `terraform refresh` do?",
    "options": {
      "A": "Updates provider versions",
      "B": "Syncs state with real infrastructure",
      "C": "Recreates resources",
      "D": "Formats code"
    },
    "answer": "B"
  },
  {
    "question": "True or False: `terraform refresh` modifies infrastructure.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is drift in Terraform?",
    "options": {
      "A": "Provider bug",
      "B": "Mismatch between state and real resources",
      "C": "Invalid syntax",
      "D": "Resource dependency"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO actions help detect drift?",
    "options": {
      "A": "terraform plan",
      "B": "terraform refresh",
      "C": "terraform fmt",
      "D": "terraform init"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Manual changes in cloud consoles can cause drift.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the purpose of output values?",
    "options": {
      "A": "Store secrets",
      "B": "Expose resource attributes",
      "C": "Define variables",
      "D": "Manage providers"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO uses are common for outputs?",
    "options": {
      "A": "Sharing values between modules",
      "B": "Displaying useful info after apply",
      "C": "Encrypting state",
      "D": "Locking resources"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Outputs can be marked as sensitive.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does `terraform graph` generate?",
    "options": {
      "A": "Execution logs",
      "B": "Dependency graph",
      "C": "State diagram",
      "D": "Cost report"
    },
    "answer": "B"
  },
  {
    "question": "True or False: `terraform graph` helps visualize dependencies.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the primary architectural difference between a 'Component' in Terraform Stacks and a standard 'Module' in traditional Terraform?",
    "options": {
      "A": "Components do not require a provider block.",
      "B": "Components are the building blocks of a Stack that share a unified lifecycle and can be orchestrated across multiple deployments (environments/regions) with different inputs.",
      "C": "Components can only be written in Python, not HCL.",
      "D": "Components are stored in the state file, while modules are not."
    },
    "answer": "B"
  },
  {
    "question": "In Terraform 1.10+, what unique property does an 'ephemeral' resource possess regarding the State file?",
    "options": {
      "A": "It is stored in a separate, encrypted .tfstate.secret file.",
      "B": "It is never persisted in the state file or plan artifacts, existing only in memory during the plan and apply phases to handle sensitive data.",
      "C": "It is deleted from the state file exactly 24 hours after creation.",
      "D": "It can only be seen by the user who created it."
    },
    "answer": "B"
  },
  {
    "question": "Which command in the 2026 unified CLI is used to initialize and manage the lifecycle of a Terraform Stack?",
    "options": {
      "A": "terraform stack-init",
      "B": "terraform stacks",
      "C": "terraform deploy --stack",
      "D": "hcp-stacks start"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of the 'deferred actions' (-allow-deferral) experimental feature in Terraform 1.12+?",
    "options": {
      "A": "To delay the payment for cloud resources until the end of the month.",
      "B": "To allow 'count' and 'for_each' arguments to have 'unknown' values during the plan phase, deferring the resolution until the apply phase.",
      "C": "To automatically retry failed resource creations after a 5-minute delay.",
      "D": "To move the 'destroy' phase to the very end of a CI/CD pipeline."
    },
    "answer": "B"
  },
  {
    "question": "When using 'Terraform Test', what does the 'skip_cleanup = true' attribute in a run block achieve?",
    "options": {
      "A": "It prevents Terraform from deleting the provider plugins.",
      "B": "It keeps the test-provisioned infrastructure alive and writes the state to disk, allowing for manual inspection or multi-stage testing.",
      "C": "It ignores all errors during the destruction phase.",
      "D": "It skips the 'terraform fmt' check."
    },
    "answer": "B"
  },
  {
    "question": "True or False: In the 2026 'Responses API' era of provider development, the Terraform Plugin Framework is preferred over SDKv2 because it natively handles 'null' vs 'unknown' states using Go generics.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the 'Terraform MCP (Model Context Protocol) Server'?",
    "options": {
      "A": "A specialized hardware server for local state storage.",
      "B": "A server that enables AI agents to securely query and interact with Terraform configurations and state for automated infrastructure management.",
      "C": "A proxy that converts HCL into Kubernetes YAML.",
      "D": "A tool used for monitoring server temperatures."
    },
    "answer": "B"
  },
  {
    "question": "How does 'Linked Stacks' simplify multi-account architectures?",
    "options": {
      "A": "By merging all cloud accounts into a single global ID.",
      "B": "By allowing data to be passed between Stacks, automatically triggering downstream Stack updates when an upstream dependency (like a network ID) changes.",
      "C": "By sharing a single credit card across all cloud providers.",
      "D": "By deleting resources in Account A when Account B is full."
    },
    "answer": "B"
  },
  {
    "question": "Which block type in a '.tfdeploy.hcl' file is used to define the specific instances (e.g., 'staging', 'prod-us-east') of a Stack?",
    "options": {
      "A": "instance",
      "B": "deployment",
      "C": "environment",
      "D": "target"
    },
    "answer": "B"
  },
  {
    "question": "In Terraform 1.11, what are 'write-only arguments' (suffixed with _wo) used for?",
    "options": {
      "A": "To create resources that cannot be deleted.",
      "B": "To securely pass ephemeral values (like passwords) to resources without them being readable from the state file after the apply.",
      "C": "To write documentation comments that the model ignores.",
      "D": "To speed up the writing of the state file to S3."
    },
    "answer": "B"
  },
  {
      "question": "What does `terraform taint` do?",
      "options": {
        "A": "Deletes a resource immediately",
        "B": "Marks a resource for recreation",
        "C": "Locks the state file",
        "D": "Forces provider reinitialization"
      },
      "answer": "B"
    },
    {
      "question": "True or False: `terraform taint` modifies the infrastructure instantly.",
      "options": {
        "A": "True",
        "B": "False"
      },
      "answer": "B"
    },
    {
      "question": "Which TWO backends support remote state locking?",
      "options": {
        "A": "S3 with DynamoDB",
        "B": "Terraform Cloud",
        "C": "Local",
        "D": "HTTP without locking"
      },
      "answer": ["A", "B"]
    },
    {
      "question": "What is the purpose of `terraform import`?",
      "options": {
        "A": "Import providers",
        "B": "Bring existing resources into state",
        "C": "Download modules",
        "D": "Sync variables"
      },
      "answer": "B"
    },
    {
      "question": "True or False: Imported resources are automatically added to `.tf` files.",
      "options": {
        "A": "True",
        "B": "False"
      },
      "answer": "B"
    },
    {
      "question": "What is a data source in Terraform?",
      "options": {
        "A": "Creates new infrastructure",
        "B": "Reads existing infrastructure data",
        "C": "Stores variables",
        "D": "Manages providers"
      },
      "answer": "B"
    },
    {
      "question": "Which TWO examples are valid data sources?",
      "options": {
        "A": "aws_ami",
        "B": "aws_vpc",
        "C": "aws_instance",
        "D": "random_id"
      },
      "answer": ["A", "B"]
    },
    {
      "question": "True or False: Data sources can create resources.",
      "options": {
        "A": "True",
        "B": "False"
      },
      "answer": "B"
    },
    {
      "question": "What does `depends_on` explicitly define?",
      "options": {
        "A": "Provider dependency",
        "B": "Resource creation order",
        "C": "State backend",
        "D": "Variable precedence"
      },
      "answer": "B"
    },
    {
      "question": "True or False: Terraform automatically infers most dependencies.",
      "options": {
        "A": "True",
        "B": "False"
      },
      "answer": "A"
    },
    {
      "question": "Which TWO scenarios require explicit `depends_on`?",
      "options": {
        "A": "Implicit attribute reference exists",
        "B": "Hidden dependencies",
        "C": "Provisioners relying on external resources",
        "D": "Simple resource creation"
      },
      "answer": ["B", "C"]
    },
    {
      "question": "What does `terraform state rm` do?",
      "options": {
        "A": "Deletes infrastructure",
        "B": "Removes resource from state only",
        "C": "Destroys provider config",
        "D": "Deletes module"
      },
      "answer": "B"
    },
    {
      "question": "True or False: `terraform state rm` destroys the actual resource.",
      "options": {
        "A": "True",
        "B": "False"
      },
      "answer": "B"
    },
    {
      "question": "What is workspace isolation used for?",
      "options": {
        "A": "Separate provider versions",
        "B": "Separate state files",
        "C": "Separate modules",
        "D": "Separate backends"
      },
      "answer": "B"
    },
    {
      "question": "Which TWO use cases fit Terraform workspaces?",
      "options": {
        "A": "Dev/Test environments",
        "B": "Multi-region deployments",
        "C": "Multiple unrelated projects",
        "D": "Simple experiments"
      },
      "answer": ["A", "D"]
    },
    {
      "question": "True or False: Workspaces are recommended for large-scale environment separation.",
      "options": {
        "A": "True",
        "B": "False"
      },
      "answer": "B"
    },
    {
      "question": "What does `terraform providers lock` generate?",
      "options": {
        "A": "State file",
        "B": "Dependency lock file",
        "C": "Backend config",
        "D": "Execution plan"
      },
      "answer": "B"
    },
    {
      "question": "True or False: `.terraform.lock.hcl` ensures consistent provider versions.",
      "options": {
        "A": "True",
        "B": "False"
      },
      "answer": "A"
    },
    {
      "question": "Which TWO Terraform commands are safe in CI pipelines?",
      "options": {
        "A": "terraform init",
        "B": "terraform plan",
        "C": "terraform apply -auto-approve",
        "D": "terraform destroy"
      },
      "answer": ["A", "B"]
    },
    {
      "question": "What is the main benefit of using Terraform Cloud?",
      "options": {
        "A": "Free providers",
        "B": "Remote state and collaboration",
        "C": "Faster execution",
        "D": "No configuration files"
      },
      "answer": "B"
    },
    {
      "question": "True or False: Terraform Cloud supports policy enforcement.",
      "options": {
        "A": "True",
        "B": "False"
      },
      "answer": "A"
    },
    {
      "question": "What is Sentinel used for?",
      "options": {
        "A": "Secrets management",
        "B": "Policy as Code",
        "C": "Monitoring",
        "D": "Logging"
      },
      "answer": "B"
    },
    {
      "question": "Which TWO benefits does Sentinel provide?",
      "options": {
        "A": "Compliance enforcement",
        "B": "Prevent unsafe changes",
        "C": "Faster plans",
        "D": "Automatic scaling"
      },
      "answer": ["A", "B"]
    },
     {
    "question": "What does `terraform init` primarily do?",
    "options": {
      "A": "Creates resources",
      "B": "Initializes backend and providers",
      "C": "Validates configuration",
      "D": "Destroys infrastructure"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Terraform uses declarative syntax.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO files commonly store variable values?",
    "options": {
      "A": "terraform.tfvars",
      "B": "*.auto.tfvars",
      "C": "outputs.tf",
      "D": "providers.tf"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is the Terraform state file used for?",
    "options": {
      "A": "Storing secrets securely",
      "B": "Mapping real infrastructure to configuration",
      "C": "Provider authentication",
      "D": "Execution logs"
    },
    "answer": "B"
  },
  {
    "question": "True or False: The state file should be committed to Git.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which command shows an execution plan?",
    "options": {
      "A": "terraform apply",
      "B": "terraform plan",
      "C": "terraform init",
      "D": "terraform refresh"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO backends are remote backends?",
    "options": {
      "A": "Local",
      "B": "S3",
      "C": "Terraform Cloud",
      "D": "Null"
    },
    "answer": ["B", "C"]
  },
  {
    "question": "What does `terraform validate` do?",
    "options": {
      "A": "Checks syntax and configuration",
      "B": "Checks provider credentials",
      "C": "Checks infrastructure drift",
      "D": "Locks the state"
    },
    "answer": "A"
  },
  {
    "question": "True or False: `terraform apply` always recreates resources.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is a Terraform module?",
    "options": {
      "A": "A provider plugin",
      "B": "A reusable set of Terraform configurations",
      "C": "A backend type",
      "D": "A state file"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO benefits do modules provide?",
    "options": {
      "A": "Reusability",
      "B": "Consistency",
      "C": "Automatic scaling",
      "D": "State encryption"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Modules can call other modules.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does `terraform fmt` do?",
    "options": {
      "A": "Formats Terraform code",
      "B": "Fixes syntax errors",
      "C": "Optimizes execution",
      "D": "Encrypts files"
    },
    "answer": "A"
  },
  {
    "question": "Which argument is used to control resource count?",
    "options": {
      "A": "for_each",
      "B": "count",
      "C": "depends_on",
      "D": "lifecycle"
    },
    "answer": "B"
  },
  {
    "question": "True or False: `count.index` starts from 1.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO statements about providers are correct?",
    "options": {
      "A": "Providers define resource types",
      "B": "Providers interact with APIs",
      "C": "Providers store state",
      "D": "Providers replace modules"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What does `required_providers` block define?",
    "options": {
      "A": "Backend settings",
      "B": "Provider source and version",
      "C": "State locking",
      "D": "Variable defaults"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Terraform supports multiple providers in one configuration.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is `terraform destroy` used for?",
    "options": {
      "A": "Delete state file only",
      "B": "Destroy managed infrastructure",
      "C": "Remove providers",
      "D": "Reset variables"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO resources can be managed by Terraform?",
    "options": {
      "A": "Cloud infrastructure",
      "B": "DNS records",
      "C": "Physical hardware BIOS",
      "D": "SaaS configurations"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Terraform can manage resources outside cloud providers.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does `terraform output` display?",
    "options": {
      "A": "Provider logs",
      "B": "Defined output values",
      "C": "Variable defaults",
      "D": "State file content"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO features help with collaboration?",
    "options": {
      "A": "Remote state",
      "B": "State locking",
      "C": "Local backend",
      "D": "Hardcoded values"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Terraform is idempotent.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does `terraform init -upgrade` do?",
    "options": {
      "A": "Upgrades Terraform CLI",
      "B": "Upgrades provider plugins and modules",
      "C": "Upgrades state file version",
      "D": "Recreates infrastructure"
    },
    "answer": "B"
  },
  {
    "question": "True or False: Terraform automatically retries failed API calls.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO Terraform features help prevent accidental destruction?",
    "options": {
      "A": "prevent_destroy",
      "B": "create_before_destroy",
      "C": "ignore_changes",
      "D": "depends_on"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "What is the purpose of the `locals` block?",
    "options": {
      "A": "Define reusable expressions",
      "B": "Store secrets",
      "C": "Configure providers",
      "D": "Create resources"
    },
    "answer": "A"
  },
  {
    "question": "True or False: Local values can reference variables and resource attributes.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What does `terraform state mv` do?",
    "options": {
      "A": "Moves infrastructure to another region",
      "B": "Renames or moves resources within state",
      "C": "Migrates backend",
      "D": "Moves variables"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO scenarios require `terraform import`?",
    "options": {
      "A": "Managing pre-existing infrastructure",
      "B": "Recovering lost state",
      "C": "Creating new resources",
      "D": "Formatting configuration files"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Imported resources are automatically destroyed on the next apply.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What is a Terraform backend responsible for?",
    "options": {
      "A": "Provider execution",
      "B": "State storage and locking",
      "C": "Variable validation",
      "D": "Module versioning"
    },
    "answer": "B"
  },
  {
    "question": "Which TWO backends support state locking?",
    "options": {
      "A": "S3 with DynamoDB",
      "B": "Terraform Cloud",
      "C": "Local backend",
      "D": "Consul"
    },
    "answer": ["A", "B"]
  },
  {
    "question": "True or False: Terraform workspaces share the same state file.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "B"
  },
  {
    "question": "What does `terraform plan -out=tfplan` do?",
    "options": {
      "A": "Saves the execution plan to a file",
      "B": "Applies changes immediately",
      "C": "Exports state",
      "D": "Locks providers"
    },
    "answer": "A"
  },
  {
    "question": "Which TWO statements about `depends_on` are TRUE?",
    "options": {
      "A": "It enforces explicit resource ordering",
      "B": "It is required for all resources",
      "C": "It handles hidden dependencies",
      "D": "It replaces implicit dependencies"
    },
    "answer": ["A", "C"]
  },
  {
    "question": "True or False: Terraform automatically parallelizes resource creation when possible.",
    "options": {
      "A": "True",
      "B": "False"
    },
    "answer": "A"
  },
  {
    "question": "What is the main risk of storing secrets directly in `.tf` files?",
    "options": {
      "A": "Slower execution",
      "B": "Exposure in state files",
      "C": "Syntax errors",
      "D": "Provider conflicts"
    },
    "answer": "B"
  }
]
    
      

def remove_duplicates(questions):
    seen = set()
    unique = []

    for q in questions:
        if q["question"] not in seen:
            seen.add(q["question"])
            unique.append(q)

    return unique


def generate_pdf(skill_name, questions):
    doc = SimpleDocTemplate(
        f"{skill_name}_Question_Bank.pdf",
        pagesize=A4
    )

    elements = []
    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    elements.append(Paragraph(f"{skill_name} Question Bank ({len(questions)} Questions)", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    for i, q in enumerate(questions, 1):
        elements.append(Paragraph(f"{i}. {q['question']}", normal_style))
        elements.append(Spacer(1, 0.1 * inch))

        for key, value in q["options"].items():
            elements.append(Paragraph(f"{key}) {value}", normal_style))
            elements.append(Spacer(1, 0.05 * inch))

        elements.append(Paragraph(f"<b>Answer:</b> {q['answer']}", normal_style))
        elements.append(Spacer(1, 0.3 * inch))

    doc.build(elements)
    print(f"✅ PDF Generated with {len(questions)} UNIQUE questions only.")


if __name__ == "__main__":
    skill = "Terraform"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
