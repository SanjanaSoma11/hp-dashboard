import MentionsChart from './MentionsChart'
import RelationshipGraph from './RelationshipGraph'
import CharacterHeatmap from './CharacterHeatmap'
import Card from '../Card'

export default function CharacterIntel({ onContextChange }) {
  return (
    <section className="p-6 space-y-4">
      <h2 className="text-lg font-semibold text-warm-100 tracking-tight">Character Intelligence</h2>

      <Card title="Mention Frequency" subtitle="Chapter-by-chapter mention counts for selected characters">
        <MentionsChart onContextChange={onContextChange} />
      </Card>

      <Card title="Mentions per 1k Words — by Book" subtitle="Avg density across chapters; colour = intensity">
        <CharacterHeatmap />
      </Card>

      <Card title="Relationships" subtitle="Co-occurrence graph — node size = total mentions; click a node for stats">
        <RelationshipGraph />
      </Card>
    </section>
  )
}
