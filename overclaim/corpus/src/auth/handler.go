package auth

import "fmt"

// AuthHandler: ordinary service helper.
func AuthHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("AuthHandler: empty id")
    }
    return "AuthHandler:" + id, nil
}

func validateAuthHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
