import { useParams } from "react-router-dom";
import { TOPICS } from "../data/topics";

export default function TopicDetail() {
  const { ideology } = useParams();

  const topic = TOPICS.find(t => t.id === ideology);

  if (!topic) return <p>Topic not found</p>;

  return (
    <>
      <h2>{topic.name}</h2>
      <p>{topic.description}</p>
      {/* later: charts, grants, orgs */}
    </>
  );
}
