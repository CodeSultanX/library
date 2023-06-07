<?php

namespace App\View\Components\books;

use Illuminate\View\Component;

class jquery_create extends Component
{
    public $models;

    /**
     * Create a new component instance.
     *
     * @return void
     */
    public function __construct($models)
    {
        $this->models = $models;
    }

    /**
     * Get the view / contents that represent the component.
     *
     * @return \Illuminate\Contracts\View\View|\Closure|string
     */
    public function render()
    {
        return view('components.books.jquery_create');
    }
}