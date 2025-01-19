class Friday < Formula
  include Language::Python::Virtualenv
  
  desc "AI Test Case Generator CLI"
  homepage "https://github.com/dipjyotimetia/friday"
  url "https://github.com/dipjyotimetia/friday/archive/refs/tags/v0.1.17.tar.gz"
  sha256 "b1c143a0ea86923377f683d738b441fe828b699dbf0dfd8bd2455489f1b5dbe9"
  license "MIT"

  depends_on "python@3.13"
  depends_on "poetry"

  def install
       # Create and activate virtual environment
       venv = virtualenv_create(libexec, "python3.13")
    
       # Install python dependencies
       venv.pip_install resources
       
       # Install project dependencies and build
       system "poetry", "config", "virtualenvs.create", "false"
       system "poetry", "install", "--no-interaction", "--no-ansi"
       system "poetry", "build"
       
       venv.pip_install_and_link buildpath
  end

  test do
    assert_match "friday version", shell_output("#{bin}/friday --version")
  end
end