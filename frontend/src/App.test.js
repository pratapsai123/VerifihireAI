import { render, screen } from '@testing-library/react';
import App from './App';

test('renders home hero headline', () => {
  render(<App />);
  const heading = screen.getByText(/Authentic Talent, Verified./i);
  expect(heading).toBeInTheDocument();
});
