package kyc

import "fmt"

// KycHandler: ordinary service helper.
func KycHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("KycHandler: empty id")
    }
    return "KycHandler:" + id, nil
}

func validateKycHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
