import { useEffect, useState } from 'react'
import css from './results.module.css'

export const FavoriteButton = ({ job_id, initialIsFavorite }) => {
  const [isFavorite, setIsFavorite] = useState(initialIsFavorite)

  useEffect(() => {
    setIsFavorite(initialIsFavorite)
  }, [initialIsFavorite])

  const handleFavorite = async () => {
    await fetch(`http://127.0.0.1:5000/api/favorites/${job_id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        isFavorite: !isFavorite
      })
    })
    setIsFavorite(!isFavorite)
  }

  return (
    <button
      onClick={handleFavorite}
      className={css.favorite}
    >
      {isFavorite ? '★' : '☆'}
    </button>
  )
}


const Results = ({ jobs }) => {
  return (
    <>
      <h2>Results</h2>
      {jobs.map((job) => (
        <article className={css.result}>
          <div className='favs'>
            <FavoriteButton job_id={job.id} initialIsFavorite={job.isFavorite} />
          </div>
          <div key={job.id}>
            <h3><a href={job['job_link']} target='_blank' rel='noreferrer'>{job.job_title} <svg xmlns="http://www.w3.org/2000/svg" width="682.7" height="682.7" version="1.0" viewBox="0 0 512 512">
              <path d="M74 511c-34-5-62-30-71-64-2-8-2-8-2-162s0-154 2-163c8-31 31-54 63-63l74-1c67 0 67 0 72 2 6 4 11 10 14 16a30 30 0 0 1-14 34c-6 4-16 4-74 4s-60 0-64 2c-6 3-12 8-15 15-2 5-2 5-2 154 0 147 0 149 2 153 3 6 8 12 15 15 5 2 5 2 154 2s149 0 154-2c6-3 11-9 14-15 2-5 2-6 2-64l1-65c1-8 5-14 11-18 6-5 9-6 16-6 11 0 21 6 26 15 3 6 3 6 3 73 0 61-1 67-2 73-5 16-11 27-21 38a83 83 0 0 1-41 25c-8 2-8 2-159 3l-158-1Zm116-172c-7-2-15-10-17-17-3-7-2-13 0-19 2-5 12-15 122-125L415 58l-54-1c-54 0-54 0-60-3a29 29 0 0 1 0-51c6-2 6-2 97-2l95 1c5 2 13 9 16 15 3 5 3 5 3 97s0 92-3 97a29 29 0 0 1-51 0c-2-5-2-5-3-60V97L334 217C223 328 213 338 209 339c-6 2-13 2-19 0Z" />
              <path fill="#242424" d="M156 455h143l72 1H85l71-1Zm-92-8-1-2 2 1 2 3-3-2Zm326 0 2-2-1 2-3 2 2-2ZM56 285V141l1 72v144l-1 72V285Zm342 85v-57l1 28v57l-1 29v-57Zm57-221V97l1 26v52l-1 27v-53ZM0 137v-1l1 1v2H0v-2Zm65-15 2-2-1 2-3 2 2-2Zm46-9h59l30 1H82l29-1Zm226-57h52l27 1H311l26-1Z" />
            </svg></a></h3>
            <p>{job.company}</p>
            <p>{job.location}</p>
            <p>Salary: {!job.salary ? 'Not provided' : job.salary}</p>
          </div>
        </article>
      ))}
    </>
  )
}

export default Results