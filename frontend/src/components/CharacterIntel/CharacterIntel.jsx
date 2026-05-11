import MentionsChart from './MentionsChart'
import RelationshipGraph from './RelationshipGraph'

export default function CharacterIntel({ onContextChange }) {
  return (
    <section className="p-6 space-y-8">
      <h2 className="text-lg font-semibold text-neutral-100 tracking-tight">Character Intelligence</h2>

      <div className="space-y-2">
        <h3 className="text-sm font-medium text-neutral-400">Mention Frequency</h3>
        <MentionsChart onContextChange={onContextChange} />
      </div>

      <div className="space-y-2">
        <h3 className="text-sm font-medium text-neutral-400">Relationships</h3>
        <RelationshipGraph data={[]} />
      </div>
    </section>
  )
}
