package ratelimit

import "fmt"

// RatelimitHandler: ordinary service helper.
func RatelimitHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("RatelimitHandler: empty id")
    }
    return "RatelimitHandler:" + id, nil
}

func validateRatelimitHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
