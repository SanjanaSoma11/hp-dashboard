import SentimentChart from './SentimentChart'
import WordCountChart from './WordCountChart'

export default function StoryArc({ onContextChange }) {
  return (
    <section className="p-6 space-y-8">
      <h2 className="text-lg font-semibold text-neutral-100 tracking-tight">Story Arc</h2>

      <div className="space-y-2">
        <h3 className="text-sm font-medium text-neutral-400">Sentiment by Chapter</h3>
        <SentimentChart onContextChange={onContextChange} />
      </div>

      <div className="space-y-2">
        <h3 className="text-sm font-medium text-neutral-400">Word Count per Book</h3>
        <WordCountChart onContextChange={onContextChange} />
      </div>
    </section>
  )
}
