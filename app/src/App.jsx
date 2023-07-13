import { useState } from 'react'
import Results from './Results'
import Favorites from './Favorites'

const App = () => {
  const [query, setQuery] = useState('')
  const [location, setLocation] = useState('')
  const [jobs, setJobs] = useState([])
  const [favorites, setFavorites] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = (e) => {
    e.preventDefault()
    setIsLoading(true)
    fetch('http://127.0.0.1:5000/run-script', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, location }),
    })
      .then((response) => response.json())
      .then((data) => {
        setJobs(data.jobs)
      })
      .catch((error) => {
        console.error(error)
        setError(error)
        setIsLoading(false)
      })
      .then(() => {
        fetch('http://127.0.0.1:5000/api/jobs')
          .then((response) => response.json())
          .then((data) => {
            setJobs(data)
            setIsLoading(false)
          })
          .catch(((error) => {
            console.error(error)
            setError(error)
          }))
      })
  }

  return (
    <div>
      <h1>Job Search</h1>
      <div className='form'>
        <label>Search:
          <input
            type='text'
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            required
          /></label>
        <label>Location:
          <input
            type='text'
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            required
          /></label>
        <button onClick={handleSearch}>Submit</button>
      </div>
      <div className='favorites'>
        <button onClick={() => {
          setIsLoading(true)
          fetch('http://127.0.0.1:5000/api/favorites')
            .then((response) => response.json())
            .then((data) => {
              setFavorites(data)
              setIsLoading(false)
            })
            .catch(((error) => {
              setError(error)
              setIsLoading(false)
            }))
        }}>Favorites</button>
      </div>
      {isLoading && <p>Loading...</p>}
      {jobs.length > 0 && <Results jobs={jobs} />}
      {favorites.length > 0 && <Favorites favorites={favorites} />}
    </div>
  )
}

export default App