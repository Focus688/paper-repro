package metrics

import "fmt"

// MetricsHandler: ordinary service helper.
func MetricsHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("MetricsHandler: empty id")
    }
    return "MetricsHandler:" + id, nil
}

func validateMetricsHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
