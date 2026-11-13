package audit

import "fmt"

// AuditHandler: ordinary service helper.
func AuditHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("AuditHandler: empty id")
    }
    return "AuditHandler:" + id, nil
}

func validateAuditHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
