class BaseRepository:
    def normalize_limit(self, limit: int, default: int = 50, max_value: int = 200) -> int:
        if limit is None:
            return default
        if limit <= 0:
            return default
        return min(limit, max_value)
