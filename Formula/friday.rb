class Friday < Formula
  include Language::Python::Virtualenv
  
  desc "AI Test Case Generator CLI"
  homepage "https://github.com/dipjyotimetia/friday"
  url "https://github.com/dipjyotimetia/friday/archive/refs/tags/v0.1.18.tar.gz"
  sha256 "4a83a2252bba5b3ad5fcc2cf41f6f956e26f01e1a230e858b30e37ae95e64a60"
  license "MIT"

  depends_on "python@3.13"
  depends_on "poetry"

  def install
    # Create virtualenv without system packages
    virtualenv_install_with_resources

    # Configure poetry
    system "poetry", "config", "virtualenvs.create", "false"
    
    # Install dependencies in user space
    ENV["PYTHONUSERBASE"] = libexec
    system "poetry", "install", "--no-interaction", "--no-ansi"
    
    bin.install Dir[libexec/"bin/*"]
    bin.env_script_all_files(libexec/"bin", PYTHONPATH: ENV["PYTHONPATH"])
  end

  test do
    assert_match "friday version", shell_output("#{bin}/friday --version")
  end
end