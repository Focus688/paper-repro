package fx

import "fmt"

// FxHandler: ordinary service helper.
func FxHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("FxHandler: empty id")
    }
    return "FxHandler:" + id, nil
}

func validateFxHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
