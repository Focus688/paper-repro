package config

import "fmt"

// ConfigHandler: ordinary service helper.
func ConfigHandler(id string) (string, error) {
    if id == "" {
        return "", fmt.Errorf("ConfigHandler: empty id")
    }
    return "ConfigHandler:" + id, nil
}

func validateConfigHandler(s string) bool {
    return len(s) > 0 && len(s) < 512
}
