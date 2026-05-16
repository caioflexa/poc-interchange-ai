import os
import sys
from typing import Dict, Any, List, Optional
from app.utils.llm_sanitizer import LLMSanitizer
from app.core.config import settings


def _ensure_cuda_libs():
    """Tenta localizar e carregar bibliotecas CUDA no venv via ctypes."""
    import ctypes

    if os.name != "posix":
        return

    venv_base = os.path.join(
        settings.BASE_DIR,
        ".venv",
        "lib",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
        "site-packages",
        "nvidia",
    )
    if not os.path.exists(venv_base):
        return

    # Ordem sugerida de carregamento
    lib_names = ["libcudart.so.12", "libcublas.so.12", "libcublasLt.so.12"]

    loaded_any = False
    for root, dirs, files in os.walk(venv_base):
        if "lib" in dirs:
            lib_path = root + "/lib"
            for name in lib_names:
                full_path = os.path.join(lib_path, name)
                if os.path.exists(full_path):
                    try:
                        ctypes.CDLL(full_path, mode=ctypes.RTLD_GLOBAL)
                        loaded_any = True
                    except Exception:
                        pass
    return loaded_any


_ensure_cuda_libs()


class LocalLLM:
    def __init__(
        self,
        model_path: Optional[str] = None,
        n_ctx: Optional[int] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        n_threads: Optional[int] = None,
        stop_tokens: Optional[List[str]] = None,
        use_gpu: Optional[bool] = None,
    ):
        try:
            from llama_cpp import Llama
        except ImportError as e:
            raise ImportError(
                "Não foi possível importar 'llama-cpp-python'. Verifique se ele está instalado corretamente com suporte a GPU."
            ) from e

        # Resolve parâmetros do settings em tempo de execução
        self.model_path = model_path or settings.LLM_MODEL_PATH
        self.n_ctx = n_ctx or settings.LLM_N_CTX
        self.max_tokens = max_tokens or settings.LLM_MAX_TOKENS
        self.temperature = (
            temperature if temperature is not None else settings.LLM_TEMPERATURE
        )
        self.n_threads = n_threads or settings.LLM_N_THREADS
        self.stop_tokens = stop_tokens or settings.LLM_STOP_TOKENS

        if use_gpu is None:
            use_gpu = settings.LLM_USE_GPU

        self.sanitizer = LLMSanitizer()

        if not os.path.exists(self.model_path):
            # Tenta um caminho relativo alternativo caso o BASE_DIR falhe
            alt_path = os.path.join(
                os.getcwd(), "models", os.path.basename(self.model_path)
            )
            if os.path.exists(alt_path):
                self.model_path = alt_path
            else:
                raise FileNotFoundError(f"Modelo não encontrado em: {self.model_path}")

        n_gpu_layers = -1 if use_gpu else 0

        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=self.n_ctx,
            n_threads=self.n_threads,
            n_gpu_layers=n_gpu_layers,
            verbose=False,
        )

        self._warm_up()

    def _warm_up(self) -> None:
        self.llm(prompt=".", max_tokens=1, temperature=0.0, stop=[])

    def _extract_text(self, response: Dict[str, Any]) -> str:
        text = response["choices"][0]["text"]
        return self.sanitizer.sanitize(text)

    def generate(self, prompt: str) -> str:
        response = self._generate_full(prompt)
        return self._extract_text(response)

    def generate_with_usage(self, prompt: str) -> Dict[str, Any]:
        """Gera texto e retorna as estatísticas de uso de tokens."""
        response = self._generate_full(prompt)
        text = self.sanitizer.sanitize(response["choices"][0]["text"])
        usage = response.get("usage", {})
        return {
            "text": text,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }

    def _generate_full(self, prompt: str) -> Dict[str, Any]:
        result = self.llm(
            prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stop=self.stop_tokens,
        )
        return result  # type: ignore

    def count_tokens(self, text: str) -> int:
        return len(self.llm.tokenize(text.encode()))
