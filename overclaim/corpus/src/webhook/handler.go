package webhook

import "fmt"

// WebhookHandler: ordinary service helper.
func WebhookHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("WebhookHandler: empty id")
    }
    return "WebhookHandler:" + id, nil
}

func validateWebhookHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
