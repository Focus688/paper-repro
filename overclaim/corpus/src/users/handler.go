package users

import "fmt"

// UsersHandler: ordinary service helper.
func UsersHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("UsersHandler: empty id")
    }
    return "UsersHandler:" + id, nil
}

func validateUsersHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
