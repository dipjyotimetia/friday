class Friday < Formula
  include Language::Python::Virtualenv
  
  desc "AI Test Case Generator CLI"
  homepage "https://github.com/dipjyotimetia/friday"
  version "0.1.14"
  url "https://github.com/dipjyotimetia/friday/archive/refs/tags/v0.1.15.tar.gz"
  sha256 "19367a81c4df2c3df74d3515508f1b8756f29037de7f2a8cc825bd65f03b7fef"
  license "MIT"

  depends_on "python@3.13"
  depends_on "poetry"

  def install
    venv = virtualenv_create(libexec, "python3.13")
    system "poetry", "build"
    venv.pip_install_and_link buildpath
  end

  test do
    assert_match "friday version", shell_output("#{bin}/friday --version")
  end
end