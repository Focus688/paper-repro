package vault

import "fmt"

// VaultHandler: ordinary service helper.
func VaultHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("VaultHandler: empty id")
    }
    return "VaultHandler:" + id, nil
}

func validateVaultHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
