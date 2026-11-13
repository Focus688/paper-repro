package refund

import "fmt"

// RefundHandler: ordinary service helper.
func RefundHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("RefundHandler: empty id")
    }
    return "RefundHandler:" + id, nil
}

func validateRefundHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
