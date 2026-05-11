export default function CharacterFilter({ characters, selected, onToggle }) {
  return (
    <div className="flex flex-wrap gap-1.5 mb-3">
      {characters.map(({ name, color }) => {
        const active = selected.has(name)
        return (
          <button
            key={name}
            onClick={() => onToggle(name)}
            className={`px-2 py-0.5 rounded text-xs font-medium transition-opacity border ${
              active ? 'opacity-100' : 'opacity-30'
            }`}
            style={{ borderColor: color, color: active ? color : '#737373' }}
          >
            {name}
          </button>
        )
      })}
    </div>
  )
}
