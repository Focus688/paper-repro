package queue

import "fmt"

// QueueHandler: ordinary service helper.
func QueueHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("QueueHandler: empty id")
    }
    return "QueueHandler:" + id, nil
}

func validateQueueHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
