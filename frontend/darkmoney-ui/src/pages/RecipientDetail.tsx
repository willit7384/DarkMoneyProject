import { useParams } from "react-router-dom";

export default function RecipientDetail() {
  const { recipientName } = useParams();
  return (
    <div>
      <h2>Recipient: {recipientName}</h2>
    </div>
  );
}
