/**
 * Motorcycle Recommendation Form Component
 * Handles user input and image upload
 */

import React, { useState } from 'react';
import { getRecommendation, fileToBase64 } from '../api';
import './RecommendationForm.css';

const RecommendationForm = ({ onRecommendationReceived, onLoading }) => {
  // Form state
  const [formData, setFormData] = useState({
    height: '',
    weight: '',
    preference: 'commute',
    generateImage: true
  });

  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  /**
   * Handle image file selection
   * @param {Event} event - File input event
   */
  const handleImageChange = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setErrors({ ...errors, image: 'Please select a valid image file' });
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setErrors({ ...errors, image: 'Image size must be less than 10MB' });
      return;
    }

    setImageFile(file);
    
    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);

    setErrors({ ...errors, image: '' });
  };

  /**
   * Handle form input change
   * @param {Event} event - Input event
   */
  const handleInputChange = (event) => {
    const { name, value, type, checked } = event.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
    // Clear error for this field
    setErrors({ ...errors, [name]: '' });
  };

  /**
   * Validate form data
   * @returns {Object} Validation errors object
   */
  const validateForm = () => {
    const newErrors = {};

    if (!imageFile) {
      newErrors.image = 'Please upload a full-body photo';
    }

    const height = parseFloat(formData.height);
    if (!formData.height || height <= 0 || height > 250) {
      newErrors.height = 'Height must be between 1 and 250 cm';
    }

    const weight = parseFloat(formData.weight);
    if (!formData.weight || weight <= 0 || weight > 300) {
      newErrors.weight = 'Weight must be between 1 and 300 kg';
    }

    if (!formData.preference) {
      newErrors.preference = 'Please select a riding preference';
    }

    return newErrors;
  };

  /**
   * Handle form submission
   * @param {Event} event - Form submit event
   */
  const handleSubmit = async (event) => {
    event.preventDefault();

    // Validate form
    const validationErrors = validateForm();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    try {
      setIsSubmitting(true);
      onLoading(true);
      setErrors({});

      // Convert image to base64
      const imageBase64 = await fileToBase64(imageFile);

      // Call API
      const recommendation = await getRecommendation({
        imageBase64,
        height: parseFloat(formData.height),
        weight: parseFloat(formData.weight),
        preference: formData.preference,
        generateImage: formData.generateImage
      });

      // Pass recommendation to parent component
      onRecommendationReceived(recommendation);

    } catch (error) {
      setErrors({
        submit: error.message || 'Failed to get recommendation. Please try again.'
      });
    } finally {
      setIsSubmitting(false);
      onLoading(false);
    }
  };

  return (
    <form className="recommendation-form" onSubmit={handleSubmit}>
      <h2>Get Your Motorcycle Recommendation</h2>

      {/* Image Upload Section */}
      <div className="form-section">
        <label htmlFor="image">Upload Full-Body Photo *</label>
        <div className="image-upload">
          <input
            type="file"
            id="image"
            accept="image/*"
            onChange={handleImageChange}
            disabled={isSubmitting}
          />
          {imagePreview && (
            <div className="image-preview">
              <img src={imagePreview} alt="Selected" />
              <button type="button" onClick={() => {
                setImageFile(null);
                setImagePreview(null);
              }}>
                Remove Image
              </button>
            </div>
          )}
        </div>
        {errors.image && <p className="error">{errors.image}</p>}
      </div>

      {/* Height Input */}
      <div className="form-section">
        <label htmlFor="height">Height (cm) *</label>
        <input
          type="number"
          id="height"
          name="height"
          value={formData.height}
          onChange={handleInputChange}
          placeholder="e.g., 175"
          min="1"
          max="250"
          disabled={isSubmitting}
        />
        {errors.height && <p className="error">{errors.height}</p>}
      </div>

      {/* Weight Input */}
      <div className="form-section">
        <label htmlFor="weight">Weight (kg) *</label>
        <input
          type="number"
          id="weight"
          name="weight"
          value={formData.weight}
          onChange={handleInputChange}
          placeholder="e.g., 75"
          min="1"
          max="300"
          disabled={isSubmitting}
        />
        {errors.weight && <p className="error">{errors.weight}</p>}
      </div>

      {/* Riding Preference */}
      <div className="form-section">
        <label htmlFor="preference">Riding Preference *</label>
        <select
          id="preference"
          name="preference"
          value={formData.preference}
          onChange={handleInputChange}
          disabled={isSubmitting}
        >
          <option value="commute">Commute - City riding</option>
          <option value="touring">Touring - Long distance</option>
          <option value="sport">Sport - Performance</option>
        </select>
        {errors.preference && <p className="error">{errors.preference}</p>}
      </div>

      {/* Generate Image Checkbox */}
      <div className="form-section checkbox">
        <label htmlFor="generateImage">
          <input
            type="checkbox"
            id="generateImage"
            name="generateImage"
            checked={formData.generateImage}
            onChange={handleInputChange}
            disabled={isSubmitting}
          />
          Generate AI image of me with the bike
        </label>
      </div>

      {/* Submit Error */}
      {errors.submit && (
        <div className="error-message">
          {errors.submit}
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        className="submit-button"
        disabled={isSubmitting}
      >
        {isSubmitting ? 'Getting Recommendation...' : 'Get Recommendation'}
      </button>
    </form>
  );
};

export default RecommendationForm;
