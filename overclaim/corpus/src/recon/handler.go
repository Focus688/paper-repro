package recon

import "fmt"

// ReconHandler: ordinary service helper.
func ReconHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("ReconHandler: empty id")
    }
    return "ReconHandler:" + id, nil
}

func validateReconHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
