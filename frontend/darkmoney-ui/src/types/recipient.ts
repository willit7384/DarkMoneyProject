export interface Recipient {
  recipient_name: string; // Represents the name of the recipient organization
  total_grants: number; // Total amount of grants received by the recipient
  grant_count: number; // Number of grants received by the recipient
  donor_name: string; // Name of the top donor giving grants to this recipient
}