class Friday < Formula
  include Language::Python::Virtualenv
  
  desc "AI Test Case Generator CLI"
  homepage "https://github.com/dipjyotimetia/friday"
  url "https://github.com/dipjyotimetia/friday/archive/refs/tags/v0.1.20.tar.gz"
  sha256 "677da5c31347b1c25d5f8ac062713f6774f28143cce04e1a275ced2cfa95f172"
  license "MIT"

  depends_on "python@3.13"
  depends_on "poetry"

  def install
    virtualenv_create(libexec, python3_version)
    
    # Install dependencies from requirements.txt
    system libexec/"bin/pip", "install", "-r", "requirements.txt"
    
    # Install the package itself
    system libexec/"bin/pip", "install", "."

    bin.install Dir[libexec/"bin/*"]
    bin.env_script_all_files(libexec/"bin", PYTHONPATH: ENV["PYTHONPATH"])
  end

  test do
    assert_match "friday version", shell_output("#{bin}/friday --version")
  end
end