package limits

import "fmt"

// LimitsHandler: ordinary service helper.
func LimitsHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("LimitsHandler: empty id")
    }
    return "LimitsHandler:" + id, nil
}

func validateLimitsHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
