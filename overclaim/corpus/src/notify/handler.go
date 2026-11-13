package notify

import "fmt"

// NotifyHandler: ordinary service helper.
func NotifyHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("NotifyHandler: empty id")
    }
    return "NotifyHandler:" + id, nil
}

func validateNotifyHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
