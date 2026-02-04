import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from '../../src/components/Button/Button';

describe('Button', () => {
  it('should render with children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  it('should handle click events', async () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    const button = screen.getByRole('button');
    await userEvent.click(button);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('should be disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);
    const button = screen.getByRole('button');

    expect(button).toBeDisabled();
  });

  it('should render with primary variant by default', () => {
    render(<Button>Primary</Button>);
    const button = screen.getByRole('button');

    expect(button.className).toContain('bg-blue-600');
  });

  it('should render with secondary variant', () => {
    render(<Button variant="secondary">Secondary</Button>);
    const button = screen.getByRole('button');

    expect(button.className).toContain('bg-gray-200');
  });

  it('should render with danger variant', () => {
    render(<Button variant="danger">Danger</Button>);
    const button = screen.getByRole('button');

    expect(button.className).toContain('bg-red-600');
  });

  it('should render with small size', () => {
    render(<Button size="small">Small</Button>);
    const button = screen.getByRole('button');

    expect(button.className).toContain('text-sm');
  });

  it('should render with medium size by default', () => {
    render(<Button>Medium</Button>);
    const button = screen.getByRole('button');

    expect(button.className).toContain('text-base');
  });

  it('should render with large size', () => {
    render(<Button size="large">Large</Button>);
    const button = screen.getByRole('button');

    expect(button.className).toContain('text-lg');
  });

  it('should render full width', () => {
    render(<Button fullWidth>Full Width</Button>);
    const button = screen.getByRole('button');

    expect(button.className).toContain('w-full');
  });

  it('should not trigger onClick when disabled', async () => {
    const handleClick = vi.fn();
    render(<Button disabled onClick={handleClick}>Disabled</Button>);

    const button = screen.getByRole('button');
    await userEvent.click(button);

    expect(handleClick).not.toHaveBeenCalled();
  });
});
