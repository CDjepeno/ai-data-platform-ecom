def _build_code_prompt(
        self,
        message: str,
        error: Optional[str],
        context: RetrievedContext,
    ) -> str:
        return (
            "Tu génères du code Python propre.\n"
            "Code uniquement.\n\n"

            f"Problème:\n{message}\n\n"
            f"Solution:\n{context['solution']}\n\n"

            "Contraintes:\n"
            "- Code exécutable\n"
            "- Typé\n"
            "- Docstring\n"
            "- Exemple\n"
        )