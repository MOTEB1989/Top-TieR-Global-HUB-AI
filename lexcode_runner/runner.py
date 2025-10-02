import yaml

from modules import fetchers, processors, renderers


def run_task(task):
    print(f"\n🚀 Running Task: {task['name']} (id={task['id']})")

    data = None
    for step in task.get("steps", []):
        if "fetch" in step:
            data = fetchers.handle_fetch(step["fetch"])
        elif "process" in step:
            data = processors.handle_process(step["process"], data)
        elif "render" in step:
            renderers.handle_render(step["render"], data)
        else:
            print(f"⚠️ Unknown step: {step}")


def main():
    with open("lexcode.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    print(f"🧠 LexCode Runner v{config.get('lexcode_version')}")
    print(f"📂 Project: {config['project']}")
    print(f"📝 {config['description']}\n")

    for task in config["tasks"]:
        run_task(task)


if __name__ == "__main__":
    main()
