# Contributing to Top-TieR-Global-HUB-AI

Thank you for your interest in contributing to the Top-TieR-Global-HUB-AI project! We appreciate your help and want to ensure a smooth and enjoyable experience for everyone involved. Below are the guidelines to follow when contributing.

## How to Contribute
1. **Fork the Repository:** Start by forking the repository to your own GitHub account.
2. **Clone Your Fork:** Clone your forked repository to your local machine.
3. **Create a New Branch:** Before making any changes, create a new branch for your feature or fix. Use a descriptive name for the branch.
   ```bash
   git checkout -b your-feature-branch
   ```
4. **Make Your Changes:** Implement your feature or fix and ensure that your code adheres to the project's coding standards.
5. **Run the local checks:** Before committing, make sure the following commands succeed:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   pytest
   yamllint .github/workflows
   bash scripts/veritas_health_check.sh
   ```
   These checks mirror the most important CI jobs (unit tests, YAML validation, and health script) so you can catch issues early.
  - By default the health script targets `http://localhost:8000/health` and `http://localhost:3000/health` (or
    `http://localhost:8080/health` when it detects a GitHub Codespaces environment). Override them with
    `VERITAS_CORE_HEALTH_URL` / `VERITAS_WEB_HEALTH_URL` or set `VERITAS_HEALTH_STRICT=false` if you only need advisory output.
6. **Commit Your Changes:** Commit your changes with a clear and descriptive commit message.
   ```bash
   git commit -m "Add a new feature"
   ```
7. **Push Your Changes:** Push your changes to your forked repository.
   ```bash
   git push origin your-feature-branch
   ```
8. **Open a Pull Request:** Go to the original repository and open a pull request. Provide a clear description of the changes you made.

## Code of Conduct
Please make sure to read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to maintain a welcoming and inclusive environment for all contributors.

## Questions or Issues?
If you have any questions or encounter issues while contributing, feel free to reach out by opening an issue in the repository or contacting the maintainers directly.

Thank you for your contributions!
