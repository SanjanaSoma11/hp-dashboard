import { createContext, useContext, useState } from 'react'

const FilterContext = createContext(null)

export function FilterProvider({ children }) {
  const [selectedBooks, setSelectedBooks] = useState([1, 2, 3, 4, 5, 6, 7])
  return (
    <FilterContext.Provider value={{ selectedBooks, setSelectedBooks }}>
      {children}
    </FilterContext.Provider>
  )
}

export function useFilter() {
  return useContext(FilterContext)
}
