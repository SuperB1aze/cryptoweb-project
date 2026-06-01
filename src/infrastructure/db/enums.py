import enum

class Role(enum.Enum):
    user = "User"
    mod = "Mod"
    admin = "Admin"

class SortOrder(enum.Enum):
    newest = "Newest"
    oldest = "Oldest"
    popular = "Popular"