package dispute

import "fmt"

// DisputeHandler: ordinary service helper.
func DisputeHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("DisputeHandler: empty id")
    }
    return "DisputeHandler:" + id, nil
}

func validateDisputeHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
