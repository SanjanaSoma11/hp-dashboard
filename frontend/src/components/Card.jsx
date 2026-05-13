export default function Card({ title, subtitle, children, className = '' }) {
  return (
    <div className={`bg-neutral-900 border border-neutral-800 rounded-lg p-5 ${className}`}>
      <div className="mb-4">
        <h3 className="text-sm font-medium text-warm-100">{title}</h3>
        {subtitle && <p className="text-xs text-warm-400 mt-0.5">{subtitle}</p>}
      </div>
      {children}
    </div>
  )
}
