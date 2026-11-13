package cache

import "fmt"

// CacheHandler: ordinary service helper.
func CacheHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("CacheHandler: empty id")
    }
    return "CacheHandler:" + id, nil
}

func validateCacheHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
