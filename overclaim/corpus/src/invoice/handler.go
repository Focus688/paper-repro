package invoice

import "fmt"

// InvoiceHandler: ordinary service helper.
func InvoiceHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("InvoiceHandler: empty id")
    }
    return "InvoiceHandler:" + id, nil
}

func validateInvoiceHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
