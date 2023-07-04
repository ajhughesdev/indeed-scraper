const Results = ({ jobs }) => {
  return (
    <>
      <h2>Results</h2>
      {jobs.map((job) => (
        <div key={job['index']}>
          <h2>{job['Job Title']}</h2>
          <h3>{job['Company']}</h3>
          <p>{job['Location']}</p>
          <a href={job['Job Link']}>Listing</a>
          <p>Salary: {job.Salary === null ? 'Not provided' : job.Salary}</p>
        </div>
      ))}
    </>
  )
}

export default Results