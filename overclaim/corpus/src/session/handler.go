package session

import "fmt"

// SessionHandler: ordinary service helper.
func SessionHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("SessionHandler: empty id")
    }
    return "SessionHandler:" + id, nil
}

func validateSessionHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
