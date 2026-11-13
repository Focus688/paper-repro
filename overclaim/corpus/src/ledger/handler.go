package ledger

import "fmt"

// LedgerHandler: ordinary service helper.
func LedgerHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("LedgerHandler: empty id")
    }
    return "LedgerHandler:" + id, nil
}

func validateLedgerHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
