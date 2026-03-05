import logging
from typing import List, Tuple, Optional
import os
from pathlib import Path

from app.services.embedding.base import EmbeddingServiceInterface

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")


EMBEDDING_DIMENSIONS = {
    "all-MiniLM-L6-v2": 384,
    "all-mpnet-base-v2": 768,
    "paraphrase-multilingual-MiniLM-L12-v2": 384,
    "paraphrase-multilingual-mpnet-base-v2": 768,
    "BAAI/bge-m3": 1024,
    "BAAI/bge-large-zh": 1024,
    "BAAI/bge-large-en": 1024,
    "BAAI/bge-base-en": 768,
    "BAAI/bge-base-zh": 768,
}


class LocalEmbeddingService(EmbeddingServiceInterface):
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        cache_folder: Optional[str] = None,
        device: str = "auto",
    ):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Install with: pip install sentence-transformers"
            )
        
        if cache_folder is None:
            cache_folder = os.environ.get(
                'XIVMIND_MODELS_CACHE',
                os.path.join(os.path.expanduser("~"), ".xivmind", "models")
            )
        
        os.makedirs(cache_folder, exist_ok=True)
        
        self.model_name = model_name
        self.cache_folder = cache_folder
        self._device_config = device
        self._resolved_device: Optional[str] = None
        self._model: Optional["SentenceTransformer"] = None
        self._model_path: Optional[str] = None
        self.dimension = EMBEDDING_DIMENSIONS.get(model_name, 384)
    
    def _get_device(self) -> str:
        """Resolve the device to use for inference."""
        if self._resolved_device is not None:
            return self._resolved_device
        
        if self._device_config == "auto":
            try:
                import torch
                if torch.cuda.is_available():
                    self._resolved_device = "cuda"
                    gpu_name = torch.cuda.get_device_name(0)
                    logger.info(f"Using CUDA GPU for embedding: {gpu_name}")
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    self._resolved_device = "mps"
                    logger.info("Using Apple MPS for embedding")
                else:
                    self._resolved_device = "cpu"
                    logger.info("Using CPU for embedding (no GPU available)")
            except ImportError:
                self._resolved_device = "cpu"
                logger.info("PyTorch not installed, using CPU for embedding")
        else:
            self._resolved_device = self._device_config
            logger.info(f"Using specified device: {self._resolved_device}")
        
        return self._resolved_device
    
    @property
    def device(self) -> str:
        """Get the resolved device."""
        return self._get_device()
    
    def _find_model_in_cache(self) -> Optional[str]:
        """Find the model in local cache folder."""
        cache_path = Path(self.cache_folder)
        if not cache_path.exists():
            return None
        
        model_folder_name = f"models--{self.model_name.replace('/', '--')}"
        model_path = cache_path / model_folder_name
        
        if model_path.exists():
            snapshots_path = model_path / "snapshots"
            if snapshots_path.exists():
                snapshots = list(snapshots_path.iterdir())
                if snapshots:
                    for snapshot in snapshots:
                        if snapshot.is_dir() and (snapshot / "config.json").exists():
                            return str(snapshot)
                    if snapshots:
                        return str(snapshots[0])
        
        return None
    
    def _find_model_in_hf_cache(self) -> Optional[str]:
        """Find the model in HuggingFace default cache."""
        cache_paths = []
        
        if os.environ.get('HF_HUB_CACHE'):
            cache_paths.append(os.environ.get('HF_HUB_CACHE'))
        
        if os.environ.get('HF_HOME'):
            cache_paths.append(os.path.join(os.environ.get('HF_HOME'), 'hub'))
        
        default_cache = os.path.join(os.path.expanduser('~'), '.cache', 'huggingface', 'hub')
        cache_paths.append(default_cache)
        
        if os.environ.get('XDG_CACHE_HOME'):
            cache_paths.append(os.path.join(os.environ.get('XDG_CACHE_HOME'), 'huggingface', 'hub'))
        
        if os.name == 'nt':
            local_app_data = os.environ.get('LOCALAPPDATA', os.environ.get('APPDATA', ''))
            if local_app_data:
                cache_paths.append(os.path.join(local_app_data, 'huggingface', 'hub'))
        
        for hf_cache in cache_paths:
            if not hf_cache or not os.path.exists(hf_cache):
                continue
            
            model_folder_name = f"models--{self.model_name.replace('/', '--')}"
            model_path = os.path.join(hf_cache, model_folder_name)
            
            if os.path.exists(model_path):
                snapshots_path = os.path.join(model_path, "snapshots")
                if os.path.exists(snapshots_path):
                    snapshots = [d for d in os.scandir(snapshots_path) if d.is_dir()]
                    if snapshots:
                        for snapshot in snapshots:
                            if os.path.exists(os.path.join(snapshot.path, "config.json")):
                                return snapshot.path
                        return snapshots[0].path
        
        return None
    
    def _is_model_cached(self) -> bool:
        """Check if model exists in any cache location."""
        return self._find_model_in_cache() is not None or self._find_model_in_hf_cache() is not None
    
    def _load_model_from_cache(self, model_path: str) -> "SentenceTransformer":
        """Load model from local cache path."""
        logger.info(f"Loading model from cache: {model_path}")
        return SentenceTransformer(
            model_path,
            cache_folder=self.cache_folder,
            device=self._get_device(),
        )
    
    def _download_model(self) -> "SentenceTransformer":
        """Download model from HuggingFace Hub."""
        logger.info(f"Downloading model: {self.model_name}")
        
        original_offline = os.environ.get('TRANSFORMERS_OFFLINE')
        original_hf_offline = os.environ.get('HF_HUB_OFFLINE')
        
        if 'TRANSFORMERS_OFFLINE' in os.environ:
            del os.environ['TRANSFORMERS_OFFLINE']
        if 'HF_HUB_OFFLINE' in os.environ:
            del os.environ['HF_HUB_OFFLINE']
        
        try:
            model = SentenceTransformer(
                self.model_name,
                cache_folder=self.cache_folder,
                device=self._get_device(),
            )
            logger.info(f"Model downloaded successfully: {self.model_name}")
            return model
        finally:
            if original_offline is not None:
                os.environ['TRANSFORMERS_OFFLINE'] = original_offline
            if original_hf_offline is not None:
                os.environ['HF_HUB_OFFLINE'] = original_hf_offline
    
    @property
    def model(self) -> "SentenceTransformer":
        if self._model is None:
            device = self._get_device()
            logger.info(f"Loading embedding model: {self.model_name}")
            
            local_cache_path = self._find_model_in_cache()
            if local_cache_path:
                logger.info("Model found in local cache, using offline mode")
                self._model = self._load_model_from_cache(local_cache_path)
                self._model_path = local_cache_path
            else:
                hf_cache_path = self._find_model_in_hf_cache()
                if hf_cache_path:
                    logger.info("Model found in HuggingFace cache, using offline mode")
                    self._model = self._load_model_from_cache(hf_cache_path)
                    self._model_path = hf_cache_path
                else:
                    logger.info("Model not found in cache, downloading from HuggingFace Hub...")
                    self._model = self._download_model()
            
            logger.info(f"Model loaded. Dimension: {self.dimension}, Device: {device}")
        return self._model
    
    def encode(self, text: str) -> Tuple[List[float], str]:
        if not text or not text.strip():
            return [0.0] * self.dimension, self.model_name
        
        try:
            embedding = self.model.encode(
                text,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            return embedding.tolist(), self.model_name
        except Exception as e:
            logger.error(f"Failed to encode text: {e}")
            return [0.0] * self.dimension, self.model_name
    
    def encode_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
    ) -> Tuple[List[List[float]], str]:
        if not texts:
            return [], self.model_name
        
        try:
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                batch_size=batch_size,
                show_progress_bar=False,
            )
            return embeddings.tolist(), self.model_name
        except Exception as e:
            logger.error(f"Failed to encode batch: {e}")
            return [[0.0] * self.dimension for _ in texts], self.model_name
    
    def get_dimension(self) -> int:
        return self.dimension
    
    def get_model_name(self) -> str:
        return self.model_name
    
    def get_device(self) -> str:
        """Get the resolved device name."""
        return self.device
    
    def is_offline_mode(self) -> bool:
        """Check if the model was loaded from cache (offline mode)."""
        return self._model_path is not None
    
    def get_cache_path(self) -> Optional[str]:
        """Get the cache path where the model was loaded from."""
        return self._model_path
