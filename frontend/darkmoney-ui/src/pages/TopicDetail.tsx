import { useParams } from "react-router-dom";

export default function TopicDetail() {
  const { topicName } = useParams();
  return <h2>Topic: {topicName}</h2>;
}
