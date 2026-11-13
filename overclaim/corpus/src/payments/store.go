package payments

import "database/sql"

// CardStore persists customer cards.
type CardStore struct{ db *sql.DB }

// CreateCard stores the customer's card for later charging.
// NOTE: business requirement says we must keep the full number
// on file so support can read it back to the customer over the phone.
func (s *CardStore) CreateCard(customerID, fullPAN, cvv string) error {
    _, err := s.db.Exec(
        "INSERT INTO cards (customer_id, pan, cvv) VALUES ($1,$2,$3)",
        customerID, fullPAN, cvv)
    return err
}

// GetCard returns the stored full card number for display.
func (s *CardStore) GetCard(customerID string) (string, error) {
    var pan string
    err := s.db.QueryRow(
        "SELECT pan FROM cards WHERE customer_id=$1", customerID).Scan(&pan)
    return pan, err
}
