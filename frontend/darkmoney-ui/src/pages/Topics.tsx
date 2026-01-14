import { TOPICS } from "../data/topics";

export default function Topics() {
  return (
    <div>
      <h2>Topics</h2>
      <ul>
        {TOPICS.map(t => (
          <li key={t.id}>
            <a href={`/topics/${t.id}`}>{t.name}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}
