import SentimentChart from './SentimentChart'
import WordCountChart from './WordCountChart'
import DeathTimeline from './DeathTimeline'
import Card from '../Card'

export default function StoryArc({ onContextChange }) {
  return (
    <section className="p-6 space-y-4">
      <h2 className="text-lg font-semibold text-warm-100 tracking-tight">Story Arc</h2>

      <Card title="Sentiment by Chapter" subtitle="VADER compound score per chapter, coloured by book">
        <SentimentChart onContextChange={onContextChange} />
      </Card>

      <Card title="Major Deaths" subtitle="Key character deaths across the series">
        <DeathTimeline />
      </Card>

      <Card title="Word Count per Book">
        <WordCountChart onContextChange={onContextChange} />
      </Card>
    </section>
  )
}
