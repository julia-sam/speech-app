import React, { useEffect, useState } from 'react'

interface Exercise {
  word_or_phrase: string
  pronunciationUrl: string
}

const PronunciationPractice = () => {
  const [categories, setCategories] = useState<string[]>([])
  const [exercises, setExercises] = useState<Exercise[]>([])

  useEffect(() => {
    fetch('http://localhost:8080/api/pronunciation_practice')
      .then((response) => response.json())
      .then((data) => setCategories(data.categories))
      .catch((error) => console.error('Error:', error))
  }, [])

  const fetchPronunciations = (category: string) => {
    fetch(`http://localhost:8080/api/pronunciation_practice/${category}`)
      .then((response) => response.json())
      .then((data) => setExercises(data)) 
      .catch((error) => console.error('Error:', error))
  };

  return (
    <div>
      <h1>English Pronunciation Practice</h1>
      <div className="categories-container">
        {categories.map((category, index) => (
          <button key={index} onClick={() => fetchPronunciations(category)} className="category-item">
            {category}
          </button>
        ))}
      </div>
      <div>
        {exercises.map((exercise, index) => (
          <div key={index}>
            <p>{exercise.word_or_phrase}</p>
            <audio controls key={exercise.pronunciationUrl}>
              <source src={exercise.pronunciationUrl} type="audio/mpeg" />
            </audio>
          </div>
        ))}
      </div>
    </div>
  )
}

export default PronunciationPractice
